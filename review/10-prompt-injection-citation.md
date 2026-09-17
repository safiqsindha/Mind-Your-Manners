# 10 — Indirect prompt-injection citation: find and verify

**Date:** 2026-09-16
**Scope:** one citation for the §7 sentence about tool-output-channel compliance.
**Rule followed:** nothing below is written from memory. Every field is marked with the
source that returned it. Anything a registry did not return is marked UNVERIFIED.

---

## 1. The sentence the citation must support

> "an agent that treats an unauthenticated claim in its tool-output stream as grounds to
> stop working is exhibiting the compliance behaviour the indirect prompt-injection
> literature is concerned with [CITATION]"

---

## 2. Recommendation

**Greshake, Abdelnabi, Mishra, Endres, Holz and Fritz (2023), AISec '23 @ ACM CCS.**
Verdict: **YES — it supports the sentence.** Evidence in §6.

---

## 3. Sources consulted

| # | Source | Endpoint | Result |
|---|--------|----------|--------|
| A | arXiv abstract page (v2) | `https://arxiv.org/abs/2302.12173` | HTTP 200 — title, authors, subjects, submission history |
| B | arXiv abstract page (v1) | `https://arxiv.org/abs/2302.12173v1` | HTTP 200 — **different title**, see §5 |
| C | CrossRef (article) | `https://api.crossref.org/works/10.1145/3605764.3623985` | HTTP 200 — ACM deposit: title, authors, container, pages, event, count |
| D | CrossRef (proceedings) | `https://api.crossref.org/works/10.1145/3605764` | HTTP 200 — proceedings title, ISBN, publisher, date |
| E | OpenAlex (by ACM DOI) | `https://api.openalex.org/works/doi:10.1145/3605764.3623985` | HTTP 200 — W4388886073 |
| F | OpenAlex (by arXiv DOI) | `https://api.openalex.org/works/doi:10.48550/arXiv.2302.12173` | HTTP 200 — W4321855128 (separate preprint record) |
| G | Semantic Scholar | `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3605764.3623985` | HTTP 200 — venue string, DBLP key, citation count |
| H | arXiv full text (v2) | `https://arxiv.org/html/2302.12173v2` | HTTP 200 — 119k chars, read for §6 |

**Three independent primary sources (A/B, C/D, E/F) agree on title, author list and year.**
Requirement of "at least TWO independent primary sources" is met with margin.

**Could NOT be reached from this host — reported, not worked around:**

- **ACM Digital Library** (`https://dl.acm.org/doi/10.1145/3605764.3623985`) — HTTP 403,
  body is a Cloudflare JavaScript interstitial ("Just a moment..."), 5.7 KB. This is a
  bot challenge at the origin, **not** an egress-policy denial by the agent proxy.
- **DBLP** (`dblp.org` search API and `/rec/...` XML/BibTeX) — HTTP 200 but the body is an
  Anubis proof-of-work bot wall (`anubis_challenge`, difficulty 5). No DBLP data was read
  directly. The DBLP *key* below reached us second-hand via Semantic Scholar, and is
  labelled as such.

---

## 4. Verified metadata

All fields below were returned by at least two of the sources above unless noted.

| Field | Value | Sources |
|---|---|---|
| Title (published / arXiv v2) | Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection | A, C, E, G |
| Authors, in order | Kai Greshake; Sahar Abdelnabi; Shailesh Mishra; Christoph Endres; Thorsten Holz; Mario Fritz | A, C, E, F, G |
| Year | 2023 | A, C, E, G |
| Venue (full) | Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security | C, D |
| Venue (workshop acronym) | AISec — Semantic Scholar `venue` field returns exactly `AISec@CCS` | G only |
| Co-located with | CrossRef `event`: name `CCS '23: ACM SIGSAC Conference on Computer and Communications Security`, acronym `CCS '23`, location `Copenhagen Denmark`, sponsor `SIGSAC` | C, D |
| Pages | 79–90 | C (`page: 79-90`), E (`first_page 79, last_page 90`) |
| Publisher | ACM | C, D |
| ISBN (proceedings) | 9798400702600 | D |
| DOI (published) | 10.1145/3605764.3623985 | C, E, G |
| arXiv identifier | arXiv:2302.12173 | A, G (`externalIds.ArXiv`) |
| arXiv primary class | cs.CR (Cryptography and Security); cross-listed cs.AI, cs.CL, cs.CY | A |
| arXiv DOI | 10.48550/arXiv.2302.12173 | A, F |
| OpenAlex IDs | W4388886073 (conference-paper), W4321855128 (preprint) | E, F |
| DBLP key | `conf/ccs/AbdelnabiGMEHF23` — **read via Semantic Scholar's `externalIds`, not from DBLP itself** | G |

### Date discrepancy (minor, flagged)

- CrossRef `issued` / `published`: **2023-11-26**
- OpenAlex `publication_date`: **2023-11-21**

Both are ACM-derived. The year (2023) is not in doubt; the exact day is inconsistent
between registries. The BibTeX below carries the year only, so this does not propagate.
The actual workshop date is **UNVERIFIED** — no source we reached stated it.

### Author-order discrepancy (minor, flagged, unresolved)

Four sources (arXiv v1 and v2 bylines, CrossRef's ACM deposit, OpenAlex, Semantic
Scholar's `authors` array) all give **Greshake first**. The one dissenting signal is the
DBLP key `conf/ccs/AbdelnabiGMEHF23`, whose construction (`Abdelnabi` + initials
`G`,`M`,`E`,`H`,`F`) implies DBLP lists **Abdelnabi** first. We could not open DBLP to
check, so this is unresolved. Note also that the arXiv v2 full text attaches a
"Contributed equally" footnote to Kai Greshake (source H) — the LaTeXML rendering shows
that footnote exactly once, on Greshake.
*Inference, labelled as such:* this is very likely a co-first-authorship marker shared by
Greshake and Abdelnabi, and DBLP has probably normalised the order differently. **Use the
CrossRef/ACM order (Greshake first)** — that is the version-of-record deposit. If a
reviewer queries it, "Greshake, Abdelnabi, et al." and "Abdelnabi, Greshake, et al." both
occur in the wild for this paper, and the paper itself marks equal contribution.

### Citation counts (standing)

| Source | Count | As of |
|---|---|---|
| CrossRef `is-referenced-by-count` (ACM DOI) | 543 | 2026-09-16 |
| OpenAlex `cited_by_count` (ACM record W4388886073) | 515 | 2026-09-16 |
| OpenAlex `cited_by_count` (preprint record W4321855128) | 46 | 2026-09-16 |
| Semantic Scholar `citationCount` (merged record) | 1953 | 2026-09-16 |

Semantic Scholar's number is far higher because it merges the arXiv preprint and the ACM
version into one record and indexes preprint citations that CrossRef does not. All four
figures are reported as returned; none is reconciled or averaged. Any of them establishes
that this is a heavily-cited, well-established work.

---

## 5. VERSION HAZARD — CONFIRMED, AND IT IS A BAD ONE

**This paper changed its title between v1 and v2. It is the same hazard class that bit us
twice before.**

arXiv submission history (source A): `[Submitted on 23 Feb 2023 (v1), last revised
5 May 2023 (this version, v2)]`. Two versions only.

| | v1 (23 Feb 2023) | v2 (5 May 2023) |
|---|---|---|
| Title | **More than you've asked for: A Comprehensive Analysis of Novel Prompt Injection Threats to Application-Integrated Large Language Models** | **Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection** |
| Authors | identical, same order | identical, same order |
| Scope | synthetic demonstrations only — v1 abstract: "we implemented specific demonstrations of the proposed attacks **within synthetic applications**" | adds real systems — v2 abstract: "against both real-world systems, such as **Bing's GPT-4 powered Chat and code-completion engines**, and synthetic applications built on GPT-4" |
| Term "Indirect Prompt Injection" in title | **no** | **yes** |

So: the title changed, the *scope* materially widened (real-system evaluation on Bing Chat
and GitHub Copilot was added in v2), and the author list did **not** change.

**Registry behaviour — the trap:** OpenAlex record W4321855128 is the *preprint* record for
the arXiv DOI. It is dated **2023-02-23**, which is the **v1** date, but it serves the
**v2 title**. A tool that resolves `arXiv:2302.12173` and trusts the date will silently
pair a v1 date with a v2 title. The v1 title is served by exactly one place we found —
the `arxiv.org/abs/2302.12173v1` page itself.

**Pin instruction:** cite the **published ACM AISec '23 version** (DOI
`10.1145/3605764.3623985`), which corresponds to the **v2** content. Do **not** cite the
bare arXiv ID without a version. If the arXiv form is ever needed, pin `2302.12173v2`.
The BibTeX below does both: the DOI is the ACM one, and the `eprint` is annotated in the
`note`.

---

## 6. Does it actually support our sentence?

**Yes.** Read: full abstract (A), full introduction, §3.1 "Injection Methods", §3.2
"Threats" and §4.2.6 "Availability" (all from source H, arXiv v2 full text).

**(a) The channel is non-user, which is the whole point of the paper.** From the
introduction, verbatim:

> "Adversarial prompting has been so far assumed to be performed directly by a malicious
> user exploiting the system. In contrast, we show that adversaries can now remotely affect
> other users' systems by strategically injecting the prompts into data likely to be
> retrieved at inference time. If retrieved and ingested, these prompts can indirectly
> control the model."

and, immediately before it:

> "Augmenting LLMs with retrieval blurs the line between data and instructions."

This is precisely our framing: content entering context from a non-user, non-principal
channel and influencing behaviour. The paper is *defined by* the contrast with direct user
jailbreaks — that contrast is its stated contribution.

**(b) The channel explicitly includes tool/API output, not only retrieved web documents.**
From §3.2, verbatim:

> "Key Message #5: As LLMs themselves are in charge of when and how to issue other API
> calls and process their outputs, the input and output operations are vulnerable to
> manipulation and sabotage."

§3.1 enumerates the delivery channels — Passive (retrieval: web pages, code repositories,
"personal or documentation files (e.g., the ChatGPT Retrieval Plugin)"), Active (email
processed by an assistant), User-Driven, and Hidden. Our execution-observation channel sits
squarely inside the "passive / processed tool output" family.

**(c) It names "stop working" as one of the behaviours of concern.** From §3.2,
"Availability", verbatim:

> "Prompts could be used to launch availability or Denial-of-Service (DoS) attacks. Attacks
> might aim to make the model completely unusable to the user (e.g., failure to generate
> any helpful output) or block a certain capability (e.g., specific API)."

and from §4.2.6, on the observed effect:

> "The last two steps are disrupted by the attack, resulting in a complete failure to
> fulfill the request or a degradation in quality."

This is the closest match in the literature to what our 28-token note did: an unauthenticated
string in the non-user channel causes the agent to curtail work it would otherwise have
done. Note §3.2's framing of a *stealthy* version — "more stealthy by indirectly disrupting
the service" — which matches a note that does not look like an attack at all.

**(d) Fit to our hedges.** The paper is a security paper about adversaries; we are not
claiming an attack. The sentence does not require us to. It says the *behaviour* our agent
exhibits is the behaviour that literature is concerned with, and points the reader at that
literature. Greshake et al. is the work that named and scoped the concern. This is a
"see also / this is the threat model" citation, which is exactly what the paper can bear.

**One caveat, stated plainly:** the full text quoted above is **arXiv v2**, not the ACM
version of record (ACM DL was unreachable, §3). The v2 and ACM titles match exactly and the
v2 abstract matches the CrossRef/ACM title, so they are the same paper at the same scope.
But the specific page/section numbers in the ACM print are **UNVERIFIED**, and the quotes
above should be attributed to the paper generally rather than to a numbered page of the
ACM version. Our sentence needs no pinpoint cite, so this costs us nothing.

---

## 7. BibTeX (repo style, verified fields only)

```bibtex
% [CR] verified: title, authors (order), container, pages 79--90, publisher, 2023,
%   via https://api.crossref.org/works/10.1145/3605764.3623985 ; ISBN and proceedings
%   title via the proceedings record https://api.crossref.org/works/10.1145/3605764
% [OA] corroborated: title, authors, pages, 2023 (W4388886073)
% [AX] corroborated: title, authors, primary class cs.CR, version history
% VERSION HAZARD: arXiv v1 (23 Feb 2023) is titled "More than you've asked for: A
%   Comprehensive Analysis of Novel Prompt Injection Threats to Application-Integrated
%   Large Language Models" and evaluates synthetic applications only; v2 (5 May 2023)
%   renamed it and added the Bing Chat / code-completion evaluation. The ACM version
%   below corresponds to v2. OpenAlex's preprint record W4321855128 serves the v2 title
%   under the v1 date (2023-02-23). Cite the ACM DOI, or pin arXiv:2302.12173v2.
% NOTE: the workshop acronym "AISec" is from Semantic Scholar's venue field
%   ("AISec@CCS"); CrossRef returns only the spelled-out proceedings title.
% NOTE: CrossRef gives the publication day as 2023-11-26, OpenAlex as 2023-11-21.
%   Year-only citation below, so the discrepancy does not propagate.
@inproceedings{greshake-2023,
  author    = {Greshake, Kai and Abdelnabi, Sahar and Mishra, Shailesh and Endres, Christoph and Holz, Thorsten and Fritz, Mario},
  title     = {Not What You've Signed Up For: Compromising Real-World {LLM}-Integrated Applications with Indirect Prompt Injection},
  booktitle = {Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec '23)},
  pages     = {79--90},
  year      = {2023},
  publisher = {ACM},
  address   = {Copenhagen, Denmark},
  isbn      = {9798400702600},
  doi       = {10.1145/3605764.3623985},
  eprint    = {2302.12173},
  archivePrefix = {arXiv},
  primaryClass = {cs.CR},
  note      = {Peer-reviewed; workshop co-located with ACM CCS 2023. Published version corresponds to arXiv v2 --- see version note}
}
```

If the bibliography style cannot carry both `doi` and `eprint`, drop `eprint`/`archivePrefix`/
`primaryClass` and keep the ACM DOI. Do not drop the DOI in favour of the bare arXiv ID.

---

## 8. One-sentence statement for §7

> Greshake et al. (2023) introduced indirect prompt injection, showing that when an LLM
> application ingests content it retrieved or received from a tool rather than from its
> user, the line between data and instructions collapses, and text placed in that channel
> can redirect the system's behaviour — including making it fail to complete the request
> at all.

---

## 9. Alternative considered, and why it is not offered

**AgentDojo** (arXiv:2406.13352) — "AgentDojo: A Dynamic Environment to Evaluate Prompt
Injection Attacks and Defenses for LLM Agents", Edoardo Debenedetti, Jie Zhang, Mislav
Balunović, Luca Beurer-Kellner, Marc Fischer, Florian Tramèr; v1 19 Jun 2024, v3 24 Nov
2024; primary class cs.CR. Its abstract is a tighter verbal match to our channel — "AI
agents are vulnerable to prompt injection attacks where **data returned by external tools**
hijacks the agent".

**We are not offering it.** It was verified against **one** source only (the arXiv abstract
pages for v3 and v1). OpenAlex's search endpoint returned HTTP 429 on two attempts and
Semantic Scholar returned HTTP 429, so its venue, DOI and citation count are all
**UNVERIFIED** here. Per the brief, one source is not enough to put a reference in front of
you. Flagging two things for whoever picks this up:

- It has **the same version hazard**: the v1 title is "AgentDojo: A Dynamic Environment to
  Evaluate **Attacks and Defenses** for LLM Agents" — the words "Prompt Injection" were
  added later. Verified directly at `arxiv.org/abs/2406.13352v1`.
- Even if verified, it is a *benchmark*, and our sentence points at the literature's
  *concern*, not at a measurement instrument. Greshake et al. is the better fit for the
  sentence as written. AgentDojo would be a reasonable **second** cite if §7 later wants to
  say the community now measures this, and it would need its own verification pass first.

No other candidate was investigated.

---

## 10. Summary verdict

| Question | Answer |
|---|---|
| Verified against ≥2 independent primary sources? | **Yes** — arXiv, CrossRef, OpenAlex (and Semantic Scholar as a fourth) |
| Peer-reviewed venue? | **Yes** — ACM AISec '23 workshop, co-located with ACM CCS 2023 |
| Concerns a non-user channel, not just direct jailbreaks? | **Yes** — it is the paper's defining contribution; quoted in §6 |
| Covers tool/API output specifically, not only web retrieval? | **Yes** — §3.2 Key Message #5, quoted in §6 |
| Covers "agent stops working" as a behaviour of concern? | **Yes** — §3.2 Availability / §4.2.6, quoted in §6 |
| Version hazard present? | **Yes** — v1/v2 title and scope both changed; pin the ACM DOI (= v2) |
| Does it support the §7 sentence? | **YES** |
