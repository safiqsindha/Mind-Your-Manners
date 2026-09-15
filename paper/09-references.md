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

**[chen-2023]** Chen et al. "Teaching Large Language Models to Self-Debug." — **⚠ Verified: NO.**
This work has no entry of its own in our literature review; it reaches us only through Huang et
al.'s description of it, and the words we quote in §6.5 ("serves as the perfect verifier") are
*Huang et al.'s prose about Self-Debug*, not a quotation from Chen et al. **The full citation
must be obtained and checked before submission**, or the reference dropped and the point made
through [huang-2024] alone.

**[cuadron-2025]** Alejandro Cuadron, Dacheng Li, Wenjie Ma, Xingyao Wang, Yichuan Wang, Siyuan
Zhuang, Shu Liu, Luis Gaspar Schroeder, Tian Xia, Huanzhi Mao, Nicholas Thumiger, Aditya Desai,
Ion Stoica, Ana Klimovic, Graham Neubig, Joseph E. Gonzalez. "The Danger of Overthinking:
Examining the Reasoning-Action Dilemma in Agentic Tasks." arXiv:2502.08235, 12 Feb 2025.
*Unrefereed preprint.* — **Verified:** full text. Cited in §5.4 and §6.7 for *premature
disengagement*, a term we deliberately decline to borrow.

**[dobariya-kumar-2025]** Om Dobariya, Akhil Kumar. "Mind Your Tone: Investigating How Prompt
Politeness Affects LLM Accuracy (short paper)." arXiv:2510.04950, 6 Oct 2025. 5 pages.
*Unrefereed preprint; comments field says submitted to Findings of ACL 2025.* Penn State. —
**Verified:** full text. **⚠ §3.7 item 2:** the variant count per level in their Table 1 is not
established from our secondary source and must be checked against the PDF. This is the paper the
study is positioned against.

**[dobariya-kumar-2026]** Om Dobariya, Akhil Kumar. "Mind Your Tone: Does Tone Alter LLM
Performance?" arXiv:2605.29027, 27 May 2026. *AMCIS 2026 (Thirty-second Americas Conference on
Information Systems, Reno) — refereed.* — **Verified:** full text. The same authors' own
re-run. Cited in §1.1, §3.3 and §7.8.

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
**Verified:** full text. Source of the *social register* definition this paper adopts, and of
§3.2's table. **⚠ §3.7 item 1:** their four non-hostile prefixes are not quoted in our source,
so §3.2's "no brevity instruction" column is an assertion pending a PDF check.

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
ACL* 12 (2024). DOI 10.1162/tacl_a_00681. *Refereed journal.* — **⚠ Verified: abstract only.**
Cited in §2.3 and §8.7 for the multi-prompt evaluation convention. Read in full before
submission or drop; [sclar-2024] carries the same point verified.

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

**[weinberger-hozez-2026]**, **[weinberger-hozez-2026v6]** Sarel Weinberger, Amir Hozez
(PointFive). "Prompt-Induced Waste in Coding Agents." arXiv:2608.01347, v1 2 Aug 2026, v6 10 Sep
2026. *Unrefereed preprint, genuinely preregistered.* — **Verified:** full text, v1 and v6.
**⚠ Version hazard:** the paper has six versions and grew roughly 8× in length; v6 reports 4,644
valid runs and **removes** several figures and quotes present in v1. **Cite v6 throughout, and
merge these two keys into one before submission** — they are the same paper and the paper
currently carries both.

**[yin-2024]** Ziqi Yin, Hao Wang, Kaito Horio, Daisuke Kawahara, Satoshi Sekine. "Should We
Respect LLMs? A Cross-Lingual Study on the Influence of Prompt Politeness on LLM Performance."
*Proceedings of the Second Workshop on Social Influence in Conversations (SICon 2024)*, ACL,
pp. 9–35. DOI 10.18653/v1/2024.sicon-1.2. *Refereed workshop paper.* — **Verified:** full text.
The largest-*n* study in this literature and the origin of the politeness-and-performance
question.

---

## Outstanding before submission

Four items, all flagged above and none of them cosmetic:

1. **[chen-2023] is unverified** and its quoted words are Huang et al.'s, not Chen et al.'s.
   Obtain the citation or drop it (§6.5).
2. **[mizrahi-2024] was read at abstract level only.** Read in full or drop; [sclar-2024]
   carries the same argument verified (§2.3, §8.7).
3. **[weinberger-hozez-2026] and [weinberger-hozez-2026v6] are one paper under two keys.**
   Merge, keeping v6.
4. **The two §3.7 primary-PDF checks** — [kumar-dobariya-2026]'s non-hostile prefixes and
   [dobariya-kumar-2025]'s variant count per level.

One further note on composition. The paper carries 22 citation keys for **21 distinct works**
(the two Weinberger & Hozez keys are the same paper — item 3 above). Of those 21, **eleven are
unrefereed preprints**, including both papers this study is most directly positioned against. That is a fact about
the state of this literature rather than about our citation practice, and it is part of why §7
argues for repeated measurement as a default.
