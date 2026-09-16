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
        return '\\cite[' + locator.strip() + ']{' + parts[0] + '}'
    return '\\cite{' + ','.join(parts) + '}'

DROP_BLOCK = re.compile(r'^> \*\*Draft status\.\*\*.*?(?=\n\n)', re.S | re.M)

made, failed = [], []
for md in sorted(SRC.glob('*.md')):
    tex = OUT / (md.stem + '.tex')
    if tex.exists():
        tex.unlink()                             # never leave a stale section behind
    txt = md.read_text()
    txt = DROP_BLOCK.sub('', txt)
    txt = CITE.sub(to_cite, txt)
    txt = re.sub(r'^#\s+', '## ', txt, count=1, flags=re.M)
    tmp = OUT / (md.stem + '.pre.md'); tmp.write_text(txt)
    r = subprocess.run(['pandoc', '-f', 'markdown+pipe_tables+tex_math_dollars', '-t', 'latex',
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
leftover = []
for f in made:
    for m in re.finditer(r'\{\[\}([a-z][a-z0-9-]*(?:[;,][^\]]*)?)\{\]\}', (OUT / f).read_text()):
        if m.group(1).split(',')[0].split(';')[0].strip() in keys:
            leftover.append((f, m.group(0)[:60]))
if leftover:
    print(f"  ERROR: {len(leftover)} unconverted citation(s):", file=sys.stderr)
    for f, s in leftover[:10]:
        print(f"    {f}: {s}", file=sys.stderr)

if failed or leftover:
    sys.exit(1)
