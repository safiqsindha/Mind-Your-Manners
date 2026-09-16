# Setup audit — three skills installed into ~/.claude/skills/

Date: 2026-09-16
Scope: what each skill reads, writes, executes, and whether it calls the network.
Status: installed, nothing run. Awaiting go-ahead for Stage 1.

---

## What I installed, and what I deliberately did not run

| Skill | Installed as | Method |
|---|---|---|
| PHY041/claude-skill-citation-checker | `~/.claude/skills/check-citations` | full copy |
| AlexWortega/ai-peer-review-skill | `~/.claude/skills/paper-review` | full copy |
| joshzyj/open-scholar-skill | repo at `~/.claude/open-scholar-skill`, 35 skills symlinked into `~/.claude/skills/`, 20 agents into `~/.claude/agents/` | per-entry symlink only |

I did **not** run `open-scholar-skill/setup.sh`. See §3.

Verified post-install:
- `~/.claude/settings.json` — still does not exist (never created)
- no `SCHOLAR_SKILL_DIR` in `.bashrc` / `.bash_profile` / `.zshrc`
- no `.env` written anywhere
- `git status` in the project: clean

---

## 1. check-citations — clean, no flags

Commit `9911ca6`. Four files: `SKILL.md`, `scripts/citation_checker.py` (25.7 KB), `tests/test_citation_checker.py`, `README.md`.

- **Reads:** one `.bib` path argument, or `rglob("*.bib")` under a directory argument. Nothing else.
- **Writes:** nothing. A grep for `open(...,'w')`, `write_text`, `mkdir`, `shutil`, `os.remove` returns zero hits. All output goes to stdout.
- **Executes:** nothing. No `subprocess`, no `eval`, no `exec`.
- **Network:** yes, three read-only HTTPS GETs per citation —
  - `api.crossref.org/works/{doi}` and `api.crossref.org/works?query.title=`
  - `api.semanticscholar.org/graph/v1/paper/search`
  - `api.openalex.org/works?filter=title.search:`
  - Header is a static `User-Agent: citation-checker/1.0`. No API key, no email, no identifying data transmitted.
- **Hooks / settings.json / writes outside ./review/:** none. SKILL.md shows a git pre-commit hook and a GitHub Action as copy-paste *examples*; it installs neither.
- **Dependency:** `requests` — present (2.33.1).
- **Behavior matches SKILL.md.** No discrepancies.

Caveats for Stage 1:
- It only reads `.bib`. The repo has no `.bib` file, so it has nothing to check until one exists.
- Its accuracy table is from a 25-item self-test. Treat `verified` as a weak positive and `not_found` as "needs manual follow-up", not as proof either way.
- "Future publication year" is one of its red-flag heuristics. Our required works are 2025–2026 and today is 2026-09-16, so this should not misfire, but watch for it on the June-2026 npj AI paper.

## 2. paper-review — one significant flag

Nine files: `SKILL.md`, `README.md`, `LICENSE`, `prompts/{reviewer,reviewer_alignment_forum,metareview}.md`, `scripts/{spawn_reviewers,arxiv_search}.py`.

- **Reads:** the paper (PDF/DOCX/txt/md) into `/tmp/paper_text.txt`; the three prompt templates; any pre-existing `review_*.md` when `overwrite=false`.
- **Writes:** `<output_dir>/review_<nato>.md`, `meta_review.md`, `concerns_table.csv`, `results.json`.
  - **FLAG — writes outside `./review/` by default.** Default is `./papers/<paper-stem>/`. I will pass `--output-dir ./review/peer-review/`.
- **Executes: FLAG — `claude --dangerously-skip-permissions --model sonnet -p`.**
  `spawn_reviewers.py` forks N (3–8) full Claude Code subprocesses with **all permission checks disabled**, each with Bash and unrestricted tool access, prompt on stdin, staggered 10 s apart. They inherit the working directory. Nothing in the script constrains them to read-only.
  SKILL.md discloses this only as "each child is a full Claude Code instance with tool access (Bash, arxiv_search, etc.)" — it never says `--dangerously-skip-permissions`. That is a documentation gap, and it is the single thing in this setup I would not run without you knowing about it.
  Mitigation if you want it: run it against a copy of the paper in a scratch directory, or accept it as-is on the grounds that the reviewer prompts only ask for reading and writing one review file.
- **Network:** indirectly but substantially. Each reviewer subprocess is a live API session. `arxiv_search.py` queries `export.arxiv.org` via the `arxiv` package (5 s delay, 4 retries, ≤8 results). Reviewer prompts make **1–3 arXiv queries mandatory** per reviewer.
- **Hooks / settings.json:** none.
- **Dependencies:** `arxiv` is **not installed**. Without it reviewers degrade silently (the prompt waives the mandatory call on `ImportError`). That matters here: the arXiv lookup is exactly what would stress-test your novelty claim, so I recommend `pip install arxiv` before Stage 3. `pypdf`/`pdftotext` are also absent, but irrelevant — the paper is Markdown, so I will concatenate `paper/*.md` and feed text directly.
- **Alignment Forum reviewer:** present and on by default (`alignment_critic=true`), one randomly-chosen panel slot, prompt at `prompts/reviewer_alignment_forum.md`, following Neel Nanda's ML-paper advice. This is what you asked for in Stage 3.

## 3. open-scholar-skill — largest footprint, several flags

v5.22.2, commit `1c62554`. 628 files: 36 skills, 20 agents, ~190 shell scripts, 50 Python scripts.

### What `setup.sh` would have done (NOT RUN)

1. **FLAG — writes `~/.claude/settings.json`.** Registers a `PreToolUse` hook `bash '<repo>/scripts/gates/pretooluse-data-guard.sh'` on matcher `Read|NotebookRead|NotebookEdit|Grep|Glob|Bash|Edit|Write|MultiEdit`, plus a `PostToolUse` hook on `Bash`. Creates the file if absent; `jq`-merges if present.
2. **FLAG — appends to your shell profile.** `export SCHOLAR_SKILL_DIR=...` into `~/.bashrc` / `~/.bash_profile` / `~/.zshrc`. Prompted, but defaults to Yes on Enter.
3. **FLAG — writes a plaintext `.env`** in the repo containing, if you answer the prompts, your CrossRef/OpenAlex email and your **HuggingFace access token**.
4. Scans `$HOME` for Zotero libraries across 7 candidate paths, including `~/Library/CloudStorage/*` and `~/Google Drive/`.
5. Offers `python3 -m pip install presidio-analyzer presidio-anonymizer spacy` + `spacy download en_core_web_lg` (~500 MB, network).
6. `mkdir ~/.claude/scholar-knowledge`.
7. `chmod +x` across the gate/phase helper scripts.
8. Symlinks skills and agents into `~/.claude/`. **This step alone is what I performed, by hand.**

### The PreToolUse guard, specifically

Worth understanding because it would directly obstruct Stage 2:

- Exit 2 = block; stderr is surfaced to the model as a refusal.
- Blocks `Read` of data-file extensions unless `<cwd>/.claude/safety-status.json` marks the file `CLEARED` / `ANONYMIZED` / `OVERRIDE`. `LOCAL_MODE` / `HALTED` / `NEEDS_REVIEW` are blocked.
- Blocks `Grep`/`Glob` that target a raw-data directory segment.
- Speed-bumps `Bash` content-dump commands (`cat`/`head`/`sed`/`awk`/`sqlite3`, python/R row dumps) against sensitive paths. Fails *open* here by design.
- An `EXIT` trap converts any crash into a block when the target looked like data — deliberately fail-closed.
- **No env-var bypass.** Disabling it means hand-editing `~/.claude/settings.json`.
- `jq` is present here (`/usr/bin/jq`), so it would not hit the hard "install jq" failure path — but it would still gate every read of your results files behind a `safety-status.json` sidecar that only `/scholar-init` creates. "Trace every number in the prose to a results file" would start failing until that sidecar existed.

### `/scholar-init` writes into your project

`data/raw`, `data/interim`, `data/processed`, `materials`, `output`, `.claude/`, `logs/`, a `.gitignore`, a `README.md`, an auto-managed rules block appended to **your `CLAUDE.md`**, and a PreToolUse hook block appended to `<project>/.codex/config.toml`. I have not run it and do not plan to.

### The two skills I'd actually use in Stage 2

- **`scholar-verify`** — 4-agent panel (verify-numerics, verify-figures, verify-logic, verify-completeness). Its ABSOLUTE RULE 1 is "never modify the manuscript or analysis outputs — this skill is read-only", and rule 6 is number-traceability with an `UNTRACEABLE (CRITICAL)` / `DERIVED-UNVERIFIED (WARNING)` split, which is a good fit for your Stage 2 ask. Declared tools include `Write`, used for its report. **Default output is `output/verify/` — outside `./review/`. I will override it.**
- **`scholar-citation`** — **not read-only.** Modes INSERT, FULL-REBUILD and CONVERT-STYLE edit the manuscript, and the skill "Saves complete draft + audit log". Declared tools: Read, Bash, WebSearch, WebFetch, Write. Under your session rules I would only ever invoke VERIFY / AUDIT / EXPORT, never INSERT or FULL-REBUILD.

### Other notes

- **34 of 36 skills declare `Write`**; `scholar-init` and `sync-docs` also declare `Edit`. All inert until invoked, but they are now all in the global skill list for every project on this machine.
- **Network, once invoked (not at install):** `scholar-citation`/`scholar-verify` use WebSearch + WebFetch; `scholar-rag` optionally fetches open-access PDFs and OpenAlex; `scholar-monitor` fetches journals/arXiv and can push to Telegram / ntfy.sh / SMTP; `scholar-simulate` and `scholar-annotate` call LLM provider APIs. The gate shell scripts themselves make no network calls — the only match in the whole `scripts/` tree was a `pip install` line inside a comment.
- **License — academic / non-commercial only.** Commercial use requires written permission from the author. The README also requests a citation (Zhang 2026, *Chinese Sociological Review*, doi 10.1080/21620555.2026.2707167). If you use it for the paper that becomes a tool-citation decision; I have not verified that DOI.

---

## Discrepancies between SKILL.md and actual behavior

Per your session rule, the one worth naming:

- **paper-review** — SKILL.md describes the reviewer subprocesses as "a full Claude Code instance with tool access" and never states that `spawn_reviewers.py` passes `--dangerously-skip-permissions`. Understated rather than wrong, but it is the gap most likely to matter to you.

`check-citations` matches its SKILL.md exactly. `open-scholar-skill`'s `setup.sh` matches its documentation (its own comments note that *earlier* versions silently skipped the hook registration the docs promised; the current version does perform it).

---

## Incidental finding, early but relevant to Stage 2

`libreoffice` / `soffice` are present at `/usr/bin/`. Your Stage 2 item about formula-graded results depending on LibreOffice recalculation is therefore testable in this environment rather than blocked. I have not run anything against it yet.

---

## Repo layout observed (your brief left these as placeholders)

- **Paper sections:** `paper/` — 10 Markdown files, `00-abstract.md` through `09-references.md`, ~144 KB total
- **Results/data:** `results/analysis/` (5 Python scripts, `regrade_manifest.json`, one `.txt` output); `results/raw/` is **empty except `.gitkeep`**; `results_archive/` also present; `RESULTS.md` at repo root is 113 KB
- **Bibliography:** none — no `.bib` anywhere in the repo
- **Prior art notes:** `Literature review/` — `01-sources.md` (116 KB), `02-synthesis.md`, `03-verification-log.md`
- **Harness:** `harness/` — `cli.py` (53 KB), `config.py` (33 KB), `tone_wrappers.py` (23 KB), `providers/`, `study1/`, `study2/`, `study3/`
- **Target venue:** still undecided (Stage 5 is blocked on your choice)
