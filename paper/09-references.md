# 9. References

Every entry below is transcribed from `Literature review/01-sources.md`, which records what was
verified and how. The **Verified** column reports that review's own tag: *full text* means the
paper was read in full and its quoted numbers checked against it; *abstract only* means it was
not. Two entries are flagged as needing a pass against the primary PDF, matching §3.7.

Venue is stated for each, because roughly half of this literature is unrefereed preprints and
that bears on how much weight a reader should give it.

---

**[balachandran-2025]** Vidhisha Balachandran, Jingya Chen, Lingjiao Chen, Shivam Garg, Neel
Joshi, Yash Lara, John Langford, Besmira Nushi, Vibhav Vineet, Yue Wu, Safoora Yousefi.
"Inference-Time Scaling for Complex Tasks: Where We Stand and What Lies Ahead."
arXiv:2504.00294, 31 Mar 2025. *Unrefereed preprint (Microsoft Research).* — **Verified:** full
text. Cited in §6.5 for oracle-assisted selection in inference-time scaling.

**[cuadron-2025]** Alejandro Cuadron, Dacheng Li, Wenjie Ma, Xingyao Wang, Yichuan Wang, Siyuan
Zhuang, Shu Liu, Luis Gaspar Schroeder, Tian Xia, Huanzhi Mao, Nicholas Thumiger, Aditya Desai,
Ion Stoica, Ana Klimovic, Graham Neubig, Joseph E. Gonzalez. "The Danger of Overthinking:
Examining the Reasoning-Action Dilemma in Agentic Tasks." arXiv:2502.08235, 12 Feb 2025.
*Unrefereed preprint.* — **Verified:** full text. Cited in §5.4 and §6.7 for *premature
disengagement*, a term we deliberately decline to borrow.

**[dobariya-kumar-2025]** Om Dobariya, Akhil Kumar. "Mind Your Tone: Investigating How Prompt
Politeness Affects LLM Accuracy (short paper)." arXiv:2510.04950, 6 Oct 2025. 5 pages.
*Unrefereed preprint; comments field says submitted to Findings of ACL 2025.* Penn State. —
**Verified:** full text. This is the paper the study is positioned against. **§3.7 item 2 is now
closed:** the prefix pool for its 50-question dataset is printed in [dobariya-kumar-2026] Table 1
and gives two or three variants per level, not one. The check went against our reading and §3.3
is weakened accordingly. Residual gap recorded in §3.3: we have seen the 2026 paper's table for
that dataset, not the 2025 paper's own.

**[dobariya-kumar-2026]** Om Dobariya, Akhil Kumar. "Mind Your Tone: Does Tone Alter LLM
Performance?" arXiv:2605.29027, 27 May 2026. *AMCIS 2026 (Thirty-second Americas Conference on
Information Systems, Reno) — refereed.* — **Verified: full text, primary PDF, read end to end.**
The same authors' own re-run: four models, two datasets (the original 50 questions at five tones;
570 MMLU questions at seven), ten runs each. Source of §3.3's complete prefix pool and of the
shared-preamble brevity instruction. Reports no token counts — do not confuse it with
[kumar-dobariya-2026], which is a different paper. Cited in §1.1, §3.3 and §7.8.

**[gandhi-2025]** Vishal Gandhi, Sagar Gandhi. "Prompt Sentiment: The Catalyst for LLM Change."
arXiv:2503.13510, 14 Mar 2025. *Unrefereed preprint.* — **Verified:** full text. Reports that
positive prompts *increase* verbosity — essay and blog responses 8.1% longer than neutral — on
single-turn tasks across five models. Cited in §5.4, where we state plainly that their dependent
variable (verbosity of one response) is not ours (steps taken on a task), so their result and our
praise effect are not in contradiction.

**[huang-2024]** Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu,
Xinying Song, Denny Zhou. "Large Language Models Cannot Self-Correct Reasoning Yet."
arXiv:2310.01798, 3 Oct 2023 (rev. 14 Mar 2024). *ICLR 2024 — refereed.* — **Verified:** full
text. Cited in §6.5.

**[kumar-dobariya-2026]** Akhil Kumar, Om Dobariya. "Understanding Tone-Dependent Inference Cost
in Large Language Models." arXiv:2607.23915, 27 Jul 2026. 25 pages. *Unrefereed preprint.* —
**Verified: full text, primary PDF, read end to end.** Source of the *social register* definition
this paper adopts, and of §3.2's two tables — their Table 2 (all seven prefixes, word counts,
VADER scores) and Table 3 (accuracy and output tokens, four models, ten runs). **§3.7 item 1 is
closed against this PDF, and it corrected us:** their Neutral prefix asks for "the single letter",
making it the most explicit output-length instruction of the seven rather than the
no-instruction baseline our draft called it. Distinct from [dobariya-kumar-2026]: different arXiv
number, author order, and dependent variable (inference cost, not accuracy).

**[lakens-2017]** Daniel Lakens. "Equivalence Tests: A Practical Primer for t Tests,
Correlations, and Meta-Analyses." *Social Psychological and Personality Science* 8(4), 2017,
355–362. DOI 10.1177/1948550617697177. *Refereed journal.* — **Verified:** full text. The
source for §2.8's TOST framing. Cited for equivalence testing and **not** [miller-2024], which
contains none.

**[li-2023]** Cheng Li, Jindong Wang, Yixuan Zhang, Kaijie Zhu, Wenxin Hou, Jianxun Lian, Fang
Luo, Qiang Yang, Xing Xie. "Large Language Models Understand and Can be Enhanced by Emotional
Stimuli." arXiv:2307.11760, 14 Jul 2023 (v7, 12 Nov 2023). Short version at LLM@IJCAI'23.
*Unrefereed preprint.* — **Verified:** full text. EmotionPrompt; source of §3.4's stimulus
table.

**[ma-2024]** Zeyao Ma, Bohan Zhang, Jing Zhang, Jifan Yu, Xiaokang Zhang, Xiaohan Zhang, Sijia
Luo, Xi Wang, Jie Tang. "SpreadsheetBench: Towards Challenging Real World Spreadsheet
Manipulation." arXiv:2406.14991, 21 Jun 2024 (rev. Oct 2024). *NeurIPS 2024 Spotlight, main
track — refereed.* — **Verified:** full text. Our substrate. Source of the five-round official
protocol (§2.1) and the evaluator audit (§2.10).

**[meincke-2025-report3]** Lennart Meincke, Ethan Mollick, Lilach Mollick, Dan Shapiro.
"Prompting Science Report 3: I'll pay you or I'll kill you — but will you care?"
arXiv:2508.00614, 1 Aug 2025. *Unrefereed technical report.* — **Verified:** full text. Cited in
§3.5. Note their comparisons are uncorrected for multiplicity, which §3.5 states.

**[miller-2024]** Evan Miller. "Adding Error Bars to Evals: A Statistical Approach to Language
Model Evaluations." arXiv:2411.00640, 1 Nov 2024. Anthropic. *Unrefereed preprint, widely
adopted.* — **Verified:** full text. Source of the clustered-standard-error treatment and the
MDE inversion (§2.4, §2.7). **Contains no equivalence framework** — see [lakens-2017].

**[mizrahi-2024]** Moran Mizrahi, Guy Kaplan, Dan Malkin, Rotem Dror, Dafna Shahaf, Gabriel
Stanovsky. "State of What Art? A Call for Multi-Prompt LLM Evaluation." *Transactions of the
Association for Computational Linguistics* 12 (2024), 933–949. DOI 10.1162/tacl_a_00681.
*Refereed journal.* — **Verified:** full text. 5,000 manually verified instruction paraphrases
(more than 175 per task) evaluated over 6.5M instances, 20 LLMs, 39 tasks, 3 benchmarks. Kendall's
*W* across prompts is below 0.85 for most tasks, so **model ranking**, not just absolute score,
depends on the template. **⚠ Scope their recommendation carefully:** it is use-case-dependent, not
a blanket call for ranges. They recommend averaging across many prompts when measuring robustness,
but comparing models on "their corresponding top-performing prompt" when developing a downstream
system, and they propose a Combined Performance Score uniting the two. §2.3 and §8.7 cite them for
the first use case, which is ours. They also find automatically generated paraphrases sufficient
for their metrics "without having to manually verify them" — relevant to §8.7's stimulus-sampling
objection, which we do not answer.

**[redundancybench]** Minyang Hu, Bo Yang, Zhinuo Zhou, Jiachen Liang, Jiahao Guo, Yiyang Yin,
Xiongwei Han. "Redundant or Necessary? A Benchmark for Detecting Redundant Steps in Agent
Trajectories." arXiv:2605.29893, 28 May 2026. *Unrefereed preprint; the anonymised code
repository indicates it is under double-blind review.* — **Verified:** full text. Source of the
term *redundant step* (§2.3). We do not compare base rates against theirs, as §2.3 states.

**[schegloff-sacks-1973]** Emanuel A. Schegloff, Harvey Sacks. "Opening up Closings."
*Semiotica* 8(4): 289–327, 1973. DOI 10.1515/semi.1973.8.4.289. *Refereed journal.* —
**Verified:** canonical text. The source for pre-closing structure (§5.1).

**[sclar-2024]** Melanie Sclar, Yejin Choi, Yulia Tsvetkov, Alane Suhr. "Quantifying Language
Models' Sensitivity to Spurious Features in Prompt Design, or: How I learned to start worrying
about prompt formatting." arXiv:2310.11324, 17 Oct 2023 (rev. Jul 2024). *ICLR 2024 —
refereed.* — **Verified:** full text. Cited for the **median 7.5-point** format spread used as
§2.7's comparator. Their widely-quoted 76 points is a single-task maximum on LLaMA-2-13B and is
explicitly a lower bound; we do not use it.

**[trivedi-2024]** Harsh Trivedi, Tushar Khot, Mareike Hartmann, Ruskin Manku, Vinty Dong,
Edward Li, Shashank Gupta, Ashish Sabharwal, Niranjan Balasubramanian. "AppWorld: A Controllable
World of Apps and People for Benchmarking Interactive Coding Agents." arXiv:2407.18901, 26 Jul
2024. *ACL 2024 (2024.acl-long.850) — refereed, Best Resource Paper.* — **Verified:** full text
plus evaluator source. Cited in §8.4 as the second substrate we did not run.

**[vaugrante-2024]** Laurène Vaugrante, Mathias Niepert, Thilo Hagendorff. "A Looming
Replication Crisis in Evaluating Behavior in Language Models? Evidence and Solutions."
arXiv:2409.20303, 30 Sep 2024. *Unrefereed preprint.* — **Verified:** full text. The template
for §7. Note their own design is single-run at temperature 0, which §7.1 states.

**[weinberger-hozez-2026]** Sarel Weinberger, Amir Hozez (PointFive). "Prompt-Induced Waste in
Coding Agents." arXiv:2608.01347. *Unrefereed preprint, genuinely preregistered.* — **Verified:**
full text, v1 and v6. **Cited at v6 (10 Sep 2026) throughout.** ⚠ The paper has six versions and
grew roughly 8× between v1 and v6; v6 reports 4,644 valid runs and removes several figures and
quotes present in v1, so a version must be named when citing it. Cited in §4.5 for the
tokens-per-step versus steps distinction, and in §5.5, where their `bounded_efficiency` arm
establishes that a stop condition in the *opening* prompt reduces agentic work — a result we do
not claim.

**[yin-2024]** Ziqi Yin, Hao Wang, Kaito Horio, Daisuke Kawahara, Satoshi Sekine. "Should We
Respect LLMs? A Cross-Lingual Study on the Influence of Prompt Politeness on LLM Performance."
*Proceedings of the Second Workshop on Social Influence in Conversations (SICon 2024)*, ACL,
pp. 9–35. DOI 10.18653/v1/2024.sicon-1.2. *Refereed workshop paper.* — **Verified:** full text.
The largest-*n* study in this literature and the origin of the politeness-and-performance
question.

---

## Outstanding before submission

**No verification items remain open.** Both §3.7 primary-PDF checks are closed, against
arXiv:2605.29027 and arXiv:2607.23915. Neither confirmed the draft as written, and both
corrections are stated in place in §3.2 and §3.3 rather than quietly absorbed: the first
strengthened the argument after exposing a mis-coding of ours, the second weakened a case we now
rest nothing on.

Five earlier items are now closed. **§3.7 item 2** (arXiv:2605.29027): its Table 1 prints two or
three variants per level for the 50-question dataset, not one — only two of six hostile variants
carry a demand, and the previous draft quoted exactly those two, so §3.3 is rewritten and the case
downgraded. **§3.7 item 1** (arXiv:2607.23915): their Table 2 is now quoted in full in §3.2; no
polite prefix constrains output length, but the *Neutral* one does, which removes the anomaly our
draft had conceded and makes the separation complete on all four models. **[chen-2023] has been
dropped**: the words §6.5 quoted for it
were Huang et al.'s prose about Self-Debug rather than a quotation from Chen et al., and the point
is made through [huang-2024] alone. **[mizrahi-2024] has been read in full**, and the entry above
now scopes their recommendation correctly — it is use-case-dependent rather than a blanket call
for ranges. **The two Weinberger & Hozez keys are merged**, cited at v6.

