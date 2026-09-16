# Stage 4 — Voice (findings only, no rewrites)

Date: 2026-09-16
Scope: all nine prose sections, excluding block quotes, tables and headings.

---

## Finding: the prose does not read as AI-written

I scanned for six pattern families — stock transitions, hedging stacks, triplet lists, inflated
adjectives, the "delve/underscore/tapestry" register, and "it is X that" constructions — across
roughly 150 KB of prose.

| Pattern family | Hits |
|---|---:|
| Stock transitions (*Moreover, Furthermore, Notably, Ultimately, In conclusion*) | **0** |
| Hedging stacks (*may potentially, suggests that it might*) | **0** |
| "Delve" register (*delve, underscore, shed light, pave the way, landscape of, testament to*) | **0** |
| "Not only … but also" | **0** |
| "It is X that/to" | 1 |
| Inflated adjectives | 14 |
| Triplet lists | 11 |

**26 flags, and on inspection almost all are false positives.** That is a genuinely low rate, and
the three zero rows are the informative ones: those are the highest-precision markers of
LLM-generated academic prose, and none of them fires anywhere in the paper.

---

## Why the flags don't hold

**All 14 "inflated adjective" hits are the word *significant* used in its statistical sense.**

> "Two of the 22 are nominally significant, against 1.1 expected under a global null" (§2.6)
> "none individually significant on 19–34 tasks" (§5.4)
> "no consistent significant effects anywhere" (§3.5)

Not one is rhetorical inflation. This is the correct technical term and the detector has no way to
tell the difference. **No action.**

**The 11 "triplet list" hits are technical enumerations, not rhetorical tricolons.**

> "identical tool name, arguments and output" (§2.3)
> "effects, direction and significance replicated" (§2.9)
> "on identical tasks, model and ceiling" (§7.4)

These name three things because there are three things. **No action.**

**Four of those eleven are in text I wrote**, not yours — the §9 entries added in Stage 1
("runs, before and after", "title, authors and version history", "authors, venue and version").
Flagging that so the count isn't read as a finding about your writing.

---

## The single flag worth a glance

`paper/05-closing-cues.md:81` (§5.3):

> **"It is important to state this as the within-pair contrast."** `Q4` alone sits **above**
> control…

"It is important to…" is the one construction here that reads as filler. It is also doing real
work — it flags a methodological point the reader would otherwise miss — so this is a preference
call, not a defect. A plainer opening ("State this as the within-pair contrast:" or "This has to
be read as the within-pair contrast") would carry the same meaning in fewer words.

**Your call entirely. I have not changed it.**

---

## What the scan cannot tell you

This is pattern-matching on surface features. It says the prose does not carry the *tells* of
generated text; it cannot certify authorship, and it would not catch AI-written prose that had
been edited into a distinctive voice. Given the paper's own subject matter you may want that
caveat stated rather than implied.

For what it is worth as a qualitative read: the paper has a recognisable and unusual voice —
short declaratives ("It landed in a receptive context."), self-penalising asides ("Two
disclosures about how we got there, because the coding is doing work"), and a habit of naming its
own errors in the same sentence as the correction. Those are not patterns a model produces
unprompted.
