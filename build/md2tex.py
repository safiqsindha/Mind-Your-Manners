"""Convert paper/*.md -> LaTeX bodies, rewriting [key] citations to \\cite{key}.

Exits nonzero if any conversion fails, and removes the stale .tex first, so a
failed pandoc run can never leave an old section silently in the PDF.
"""
import re, shutil, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC  = ROOT / 'paper'
OUT  = ROOT / 'build' / 'sections'
BIB_SRC = ROOT / 'review' / 'references.bib'      # canonical
BIB_DST = ROOT / 'build'  / 'references.bib'      # what bibtex reads
OUT.mkdir(parents=True, exist_ok=True)

# Single source of truth: copy the canonical bib into the build dir every run,
# so \cite keys and the bibliography can never drift apart.
shutil.copyfile(BIB_SRC, BIB_DST)
keys = set(re.findall(r'^@\w+\{([^,]+),', BIB_SRC.read_text(), re.M))

# [key] | [key-a; key-b] | [key, Table 3]  ->  \cite{key} | \cite{a,b} | \cite[Table 3]{key}
CITE = re.compile(r'\[([a-z][a-z0-9;\- ]*?)(?:,\s*([^\]]+?))?\]')

def to_cite(m):
    parts = [p.strip() for p in m.group(1).split(';')]
    if not parts or not all(p in keys for p in parts):
        return m.group(0)
    locator = m.group(2)
    if locator:
        if len(parts) > 1:                       # \cite[loc]{a,b} is ambiguous; leave alone
            return m.group(0)
        # A locator that itself contains a citation key means the bracket held
        # more than one citation and the regex split it in the wrong place --
        # e.g. "[a, Table 9; b]" would otherwise become \cite[Table 9; b]{a},
        # burying b inside a locator string where it can never resolve. Refuse
        # it so the unconverted-citation scan below reports it.
        if any(tok.strip(' ;,.') in keys for tok in re.split(r'[;,\s]+', locator)):
            return m.group(0)
        return '\\cite[' + locator.strip() + ']{' + parts[0] + '}'
    return '\\cite{' + ','.join(parts) + '}'

DROP_BLOCK = re.compile(r'^> \*\*Draft status\.\*\*.*?(?=\n\n)', re.S | re.M)
# 00-abstract.md repeats the paper title and an author placeholder; main.tex already
# sets both via \maketitle, so strip them rather than render them twice.
DROP_TITLE   = re.compile(r'\A#\s+Mind your manners.*?\n', re.M)
DROP_AUTHORS = re.compile(r'^\*\*Authors\.\*\*.*?\n', re.M)

made, failed = [], []
for md in sorted(SRC.glob('*.md')):
    tex = OUT / (md.stem + '.tex')
    if tex.exists():
        tex.unlink()                             # never leave a stale section behind
    txt = md.read_text()
    txt = DROP_BLOCK.sub('', txt)
    if md.stem == '00-abstract':
        txt = DROP_TITLE.sub('', txt)
        txt = DROP_AUTHORS.sub('', txt)
        txt = re.sub(r'\A(?:\s*---\s*\n)+', '', txt)   # rule that separated the stripped front matter
    if md.stem == '09-references':
        # In the annotated bibliography each entry OPENS with **[key]** as its own
        # label. Those are labels, not citations: converting them rendered the
        # appendix as "[21] [23] [22]" -- natbib numbers, in citation order rather
        # than entry order. Protect the line-initial label, convert the rest (the
        # genuine cross-references between entries, e.g. "see [lakens-2017]").
        LABEL = re.compile(r'^(\*\*)\[([a-z][a-z0-9-]*)\](\*\*)', re.M)
        txt = LABEL.sub(lambda m: m.group(1) + '\x00' + m.group(2) + '\x01' + m.group(3), txt)
        txt = CITE.sub(to_cite, txt)
        txt = txt.replace('\x00', '[').replace('\x01', ']')
    else:
        txt = CITE.sub(to_cite, txt)
    # Heading levels are passed through untouched: with --top-level-division=section
    # pandoc already maps # -> \section and ## -> \subsection. Demoting them flattened
    # the whole document to subsections. The source's own numbering ("1.2 What we did")
    # is kept and LaTeX's generated numbering suppressed in main.tex, because the prose
    # is full of §2.4-style cross-references tied to those exact numbers.
    tmp = OUT / (md.stem + '.pre.md'); tmp.write_text(txt)
    r = subprocess.run(['pandoc', # tex_math_dollars is ON by default in pandoc's markdown; dropping "+tex_math_dollars"
                        # does NOT disable it -- an extension is removed only with a leading "-".
                        # An earlier commit here claimed otherwise and was wrong: $x^2$ still
                        # became \(x^2\). Disabled explicitly below. The prose has no inline
                        # math but does carry dollar amounts ($48.47, $1B, $0.70), and a pair of
                        # them can be read as math whenever the closing $ has a non-space to its
                        # left and no digit to its right.
                        '-f', 'markdown-tex_math_dollars+pipe_tables', '-t', 'latex',
                        '--top-level-division=section', '-o', str(tex), str(tmp)],
                       capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    if r.returncode or not tex.exists():
        print(f"  FAIL {md.name}: {r.stderr.strip()[:300]}", file=sys.stderr)
        failed.append(md.name); continue
    tex.write_text(tex.read_text().replace('\\tightlist', ''))
    made.append(tex.name)

n_cite = sum(len(re.findall(r'\\cite(?:\[[^\]]*\])?\{', (OUT / f).read_text())) for f in made)
print(f"converted {len(made)} sections; {n_cite} \\cite commands; bib synced -> {BIB_DST.name}")

# Any citation-key-looking bracket left unconverted is a silent PDF defect.
# The annotated bibliography's entry labels are deliberately left unconverted
# (see above); they surface as \textbf{{[}key{]}} and must not be reported here.
LABEL_TEX = re.compile(r'\\textbf\{\{\[\}[a-z][a-z0-9-]*\{\]\}\}')
leftover = []
for f in made:
    body = (OUT / f).read_text()
    if f == '09-references.tex':
        body = LABEL_TEX.sub('', body)
    for m in re.finditer(r'\{\[\}([a-z][a-z0-9-]*(?:[;,][^\]]*)?)\{\]\}', body):
        if m.group(1).split(',')[0].split(';')[0].strip() in keys:
            leftover.append((f, m.group(0)[:60]))
if leftover:
    print(f"  ERROR: {len(leftover)} unconverted citation(s):", file=sys.stderr)
    for f, s in leftover[:10]:
        print(f"    {f}: {s}", file=sys.stderr)

if failed or leftover:
    sys.exit(1)
