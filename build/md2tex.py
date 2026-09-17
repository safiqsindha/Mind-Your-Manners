"""Convert a directory of *.md -> LaTeX bodies, rewriting [key] citations to \\cite{key}.

Exits nonzero if any conversion fails, and removes the stale .tex first, so a
failed pandoc run can never leave an old section silently in the PDF.

Defaults to paper/ -> build/sections (the full manuscript). The workshop carve
passes its own pair, so both documents go through exactly one converter and one
citation guard; a second copy of this file would be a second place for the
rendering defects this script exists to catch.

Nothing runs at import: the table-width logic below is unit tested, and a module
that reads sys.argv and shells out to pandoc on import cannot be imported.

  python3 build/md2tex.py [SRC_DIR] [OUT_DIR]
"""
import re, shutil, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BIB_SRC = ROOT / 'review' / 'references.bib'      # canonical
BIB_DST = ROOT / 'build'  / 'references.bib'      # what bibtex reads
SRC = OUT = None                                  # resolved in run()

# [key] | [key-a; key-b] | [key, Table 3]  ->  \cite{key} | \cite{a,b} | \cite[Table 3]{key}
CITE = re.compile(r'\[([a-z][a-z0-9;\- ]*?)(?:,\s*([^\]]+?))?\]')


def to_cite(m, keys):
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


# --- table column widths ----------------------------------------------------
# pandoc is asked below for natural-width table columns (--columns above the
# longest source row). That is what a table of labels and numbers wants: given a
# fixed fraction of \linewidth instead, pandoc sizes each column from the dash
# counts in the markdown separator row -- which have no relation to what the
# cells hold -- and LaTeX then wraps a three-word header onto three lines. Across
# this manuscript that cost three pages.
#
# A natural-width column holding a sentence, though, runs off the page: 757pt
# past the right margin, in the worst case measured here. So the few tables that
# need to wrap get their widths back below, computed from the cells.
LONGTABLE = re.compile(
    r'(\\begin\{longtable\}\[\]\{@\{\})([lrc]+)(@\{\}\}.*?)(\\end\{longtable\})', re.S)
CELL_SPLIT = re.compile(r'(?<!\\)&')
# longtable scaffolding shares lines with the cells and is not content.
SCAFFOLD = re.compile(r'@\{\}\}|\\(?:top|mid|bottom)rule|\\noalign\{\}|'
                      r'\\end(?:head|lastfoot|firsthead|firstfoot)')
# Markup is not width: \textbf{94.4\%} is fifteen source characters and five
# printed ones, and counting the source would wrap tables that fit.
MARKUP = [
    (re.compile(r'\\(?:textbf|textit|emph|texttt|textsc)\{([^{}]*)\}'), r'\1'),
    (re.compile(r'\\cite\{[^{}]*\}'), '[00]'),
    (re.compile(r'\\textless\{\}|\\textgreater\{\}'), '<'),
    (re.compile(r'\\[%&$#_]'), 'x'),
    (re.compile(r'---'), '-'),
    (re.compile(r'\\[a-zA-Z]+\{?|\}'), ''),
]
# Counting characters is a proxy for typeset width, and deliberately generous:
# wrapping a table that would have fitted costs a few lines, not wrapping one
# that does not fit puts text off the page.
MAX_CELL = 55       # a cell this long holds prose, not a label
MAX_TOTAL = 92      # printed characters that fit across the text block at 10pt
MONO_WIDTH = 1.35   # a monospace character against the body font's average
ALIGN = {'l': r'>{\raggedright\arraybackslash}',
         'r': r'>{\raggedleft\arraybackslash}',
         'c': r'>{\centering\arraybackslash}'}


def _visible_text(cell: str) -> str:
    """The cell with LaTeX markup removed, for measuring printed width."""
    for pattern, repl in MARKUP:
        cell = pattern.sub(repl, cell)
    return cell.strip()


def _visible(cell: str) -> int:
    return len(_visible_text(cell))


def _rows(body: str) -> list[list[str]]:
    rows = []
    for line in body.split('\\\\\n'):
        line = SCAFFOLD.sub('', line).strip()
        if '&' not in line:
            continue
        rows.append([c.strip() for c in CELL_SPLIT.split(line)])
    return rows


def widen(tex: str) -> str:
    """Give p{} widths back to the tables whose cells need to wrap."""
    def fix(m):
        open_, spec, body, close = m.groups()
        ncols = len(spec)
        rows = [r for r in _rows(body) if len(r) == ncols]
        widths = [0] * ncols
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], _visible(cell))
        total = sum(widths)
        if total == 0 or (max(widths) <= MAX_CELL and total <= MAX_TOTAL):
            return m.group(0)                      # natural widths are fine

        # A proportional share can come out narrower than the column's longest
        # unbreakable token -- an arm name like Q1_praise_assistant, set in a
        # monospace face with no hyphenation point -- which then runs off the
        # page however narrow the rest of the table is. Floor each column at its
        # own longest token and renormalise.
        floors = [0.0] * ncols
        for row in rows:
            for i, cell in enumerate(row):
                mono = MONO_WIDTH if '\\texttt' in cell else 1.0
                for token in _visible_text(cell).split():
                    floors[i] = max(floors[i], len(token) * mono / MAX_TOTAL)
        # Give every column its floor first, then share what is left in
        # proportion to the cells. Scaling a floored width back down afterwards
        # would undo the floor, which is the bug this replaces.
        free = 1.0 - sum(floors)
        if free > 0:
            fracs = [f + free * (w / total) for f, w in zip(floors, widths)]
        else:                                      # floors alone overflow: best effort
            fracs = [f / sum(floors) for f in floors]
        cols = ''.join(
            f'{ALIGN[a]}p{{(\\linewidth - {2 * ncols}\\tabcolsep) * \\real{{{f:.4f}}}}}'
            for a, f in zip(spec, fracs))
        return open_ + cols + body + close
    return LONGTABLE.sub(fix, tex)


def run(argv):
    """Convert SRC/*.md to OUT/*.tex. Exits nonzero on any failure."""
    global SRC, OUT
    args = [a for a in argv if not a.startswith('-')]
    SRC = (ROOT / args[0]) if len(args) > 0 else ROOT / 'paper'
    OUT = (ROOT / args[1]) if len(args) > 1 else ROOT / 'build' / 'sections'
    if not SRC.is_dir():
        sys.exit(f"no such source directory: {SRC}")
    if shutil.which('pandoc') is None:
        sys.exit("pandoc is not installed; this script shells out to it "
                 "(apt-get install pandoc). CI installs it explicitly.")
    OUT.mkdir(parents=True, exist_ok=True)

    # Single source of truth: copy the canonical bib into the build dir every run,
    # so \cite keys and the bibliography can never drift apart.
    shutil.copyfile(BIB_SRC, BIB_DST)
    keys = set(re.findall(r'^@\w+\{([^,]+),', BIB_SRC.read_text(), re.M))

    # --columns must exceed the longest table row in the sources; see the note on
    # table widths above for what happens below the threshold.
    longest = max((len(ln) for md in SRC.glob('*.md')
                   for ln in md.read_text().splitlines() if ln.startswith('|')),
                  default=0)
    columns = max(120, longest + 20)

    made, failed = [], []
    for md in sorted(SRC.glob('*.md')):
        tex = OUT / (md.stem + '.tex')
        if tex.exists():
            tex.unlink()                         # never leave a stale section behind
        txt = md.read_text()
        txt = DROP_BLOCK.sub('', txt)
        if md.stem == '00-abstract':
            txt = DROP_TITLE.sub('', txt)
            txt = DROP_AUTHORS.sub('', txt)
            txt = re.sub(r'\A(?:\s*---\s*\n)+', '', txt)   # rule after the stripped front matter
        txt = CITE.sub(lambda m: to_cite(m, keys), txt)
        # Heading levels are passed through untouched: with --top-level-division=section
        # pandoc already maps # -> \section and ## -> \subsection. Demoting them flattened
        # the whole document to subsections. The source's own numbering ("1.2 What we did")
        # is kept and LaTeX's generated numbering suppressed in main.tex, because the prose
        # is full of §2.4-style cross-references tied to those exact numbers.
        tmp = OUT / (md.stem + '.pre.md'); tmp.write_text(txt)
        r = subprocess.run(
            ['pandoc',  # tex_math_dollars is ON by default in pandoc's markdown; dropping
                        # "+tex_math_dollars" does NOT disable it -- an extension is removed
                        # only with a leading "-". An earlier commit here claimed otherwise
                        # and was wrong: $x^2$ still became \(x^2\). Disabled explicitly
                        # below. The prose has no inline math but does carry dollar amounts
                        # ($48.47, $1B, $0.70), and a pair of them can be read as math
                        # whenever the closing $ has a non-space to its left.
             '-f', 'markdown-tex_math_dollars+pipe_tables', '-t', 'latex',
             f'--columns={columns}',
             '--top-level-division=section', '-o', str(tex), str(tmp)],
            capture_output=True, text=True)
        tmp.unlink(missing_ok=True)
        if r.returncode or not tex.exists():
            print(f"  FAIL {md.name}: {r.stderr.strip()[:300]}", file=sys.stderr)
            failed.append(md.name); continue
        tex.write_text(widen(tex.read_text().replace('\\tightlist', '')))
        made.append(tex.name)

    n_cite = sum(len(re.findall(r'\\cite(?:\[[^\]]*\])?\{', (OUT / f).read_text())) for f in made)
    wrapped = sum(len(re.findall(r'\\real\{', (OUT / f).read_text())) for f in made)
    print(f"converted {len(made)} sections; {n_cite} \\cite commands; "
          f"{wrapped} wrapped table columns; bib synced -> {BIB_DST.name}")

    # Any citation-key-looking bracket left unconverted is a silent PDF defect.
    leftover = []
    for f in made:
        body = (OUT / f).read_text()
        for m in re.finditer(r'\{\[\}([a-z][a-z0-9-]*(?:[;,][^\]]*)?)\{\]\}', body):
            if m.group(1).split(',')[0].split(';')[0].strip() in keys:
                leftover.append((f, m.group(0)[:60]))
    if leftover:
        print(f"  ERROR: {len(leftover)} unconverted citation(s):", file=sys.stderr)
        for f, s in leftover[:10]:
            print(f"    {f}: {s}", file=sys.stderr)

    if failed or leftover:
        sys.exit(1)


if __name__ == '__main__':
    run(sys.argv[1:])
