"""Convert paper/*.md -> LaTeX bodies, rewriting [key] citations to \cite{key}."""
import re, subprocess, pathlib, sys

SRC = pathlib.Path('paper'); OUT = pathlib.Path('build/sections'); OUT.mkdir(parents=True, exist_ok=True)
BIB = pathlib.Path('review/references.bib')
keys = set(re.findall(r'^@\w+\{([^,]+),', BIB.read_text(), re.M))

CITE = re.compile(r'\[([a-z][a-z0-9;\- ]*)\]')
def to_cite(m):
    parts = [p.strip() for p in m.group(1).split(';')]
    if parts and all(p in keys for p in parts):
        return '\\cite{' + ','.join(parts) + '}'
    return m.group(0)

DROP_BLOCK = re.compile(r'^> \*\*Draft status\.\*\*.*?(?=\n\n)', re.S | re.M)

made = []
for md in sorted(SRC.glob('*.md')):
    txt = md.read_text()
    txt = DROP_BLOCK.sub('', txt)            # remove draft-status admonitions
    txt = CITE.sub(to_cite, txt)             # [key] -> \cite{key}
    txt = re.sub(r'^#\s+', '## ', txt, count=1, flags=re.M)   # demote H1 -> section
    tmp = OUT / (md.stem + '.pre.md'); tmp.write_text(txt)
    tex = OUT / (md.stem + '.tex')
    r = subprocess.run(['pandoc','-f','markdown+pipe_tables+tex_math_dollars','-t','latex',
                        '--top-level-division=section','-o',str(tex),str(tmp)],
                       capture_output=True, text=True)
    if r.returncode: print(f"  !! {md.name}: {r.stderr[:200]}"); continue
    body = tex.read_text()
    body = body.replace('\\tightlist','')
    tex.write_text(body); made.append(tex.name); tmp.unlink()
print(f"converted {len(made)} sections")
n = sum(len(re.findall(r'\\cite\{', (OUT/f).read_text())) for f in made)
print(f"\\cite commands emitted: {n}")
