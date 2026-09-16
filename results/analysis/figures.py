#!/usr/bin/env python3
"""Build the paper's two figures from computed contrasts, not typed numbers.

Both figures are forest plots of turn-count effects, because in both cases the
data's job is *delta against a baseline* -- how far each arm moves the agent
from the control interjection, and whether the interval clears zero. That job
takes a diverging encoding: blue for arms that shorten the trajectory, red for
arms that lengthen it, grey for arms whose effect does not survive the §2.6
correction.

Every number is read from `turn_count_family.json`, which
`turn_count_family.py` computes; nothing here is transcribed from the
manuscript's tables. That is deliberate. `tests/test_analysis_scripts.py`
already pins one script for having hardcoded its own summary numbers as string
literals, and a figure is the easiest place in a paper for that to happen
again and the hardest place for a reader to catch it.

Print safety: colour is never the only channel. Significance is also carried by
marker fill (solid = survives Benjamini-Hochberg, hollow = does not), every row
is directly labelled with its estimate and interval in a right-hand gutter, and
the two figures are legible in greyscale.

Outputs: build/figures/demand-vs-register.pdf, build/figures/closing-cue.pdf
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / "results" / "analysis"
FAMILY = ANALYSIS / "turn_count_family.json"
FIGURES = ROOT / "build" / "figures"

sys.path.insert(0, str(ROOT))
from harness.stats import benjamini_hochberg  # noqa: E402

# Diverging poles from the validated palette; grey is the de-emphasis role, not
# a third series. Validated: adjacent CVD dE 21.6 (protan), normal-vision 32.3,
# both poles >= 3:1 on the light surface.
SHORTENS = "#2a78d6"
LENGTHENS = "#e34948"
MUTED = "#8a8984"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#dcdbd6"

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK_2,
    "ytick.color": INK,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "pdf.fonttype": 42,  # embed TrueType, not Type 3 -- most venues require it
})


def load_family() -> dict:
    """The computed contrasts, regenerating them if this is a fresh checkout."""
    if not FAMILY.exists():
        subprocess.run(
            [sys.executable, str(ANALYSIS / "turn_count_family.py")],
            check=True, cwd=str(ROOT), stdout=subprocess.DEVNULL,
        )
    return json.loads(FAMILY.read_text())


def indexed(family: dict) -> dict[str, dict]:
    """Every contrast in both families, keyed by its full label."""
    out = {}
    for fam in ("arm_vs_control", "within_design_section5"):
        for c in family[fam]["contrasts"]:
            out[c["contrast"]] = c
    return out


def bh_verdicts(family: dict) -> dict[str, bool]:
    """Survives BH at the family's own alpha, computed per family, not globally.

    The two families are corrected separately and for the reason §2.6 gives, so
    a figure must not silently pool them into one 24-test family.
    """
    alpha = family["alpha"]
    verdict = {}
    for fam in ("arm_vs_control", "within_design_section5"):
        rows = family[fam]["contrasts"]
        results = benjamini_hochberg([r["p"] for r in rows], alpha=alpha)
        for r, res in zip(rows, results):
            verdict[r["contrast"]] = res.significant
    return verdict


def forest(ax, rows, contrasts, verdicts, *, xlabel):
    """One forest panel. `rows` is [(display label, contrast key), ...], top-down."""
    ys = list(range(len(rows)))[::-1]
    for y, (label, key) in zip(ys, rows):
        c = contrasts[key]
        est, lo, hi = c["estimate"], c["ci_lo"], c["ci_hi"]
        survives = verdicts[key]
        colour = MUTED if not survives else (SHORTENS if est < 0 else LENGTHENS)
        ax.plot([lo, hi], [y, y], color=colour, linewidth=2,
                solid_capstyle="round", zorder=2)
        ax.plot([est], [y], marker="o", markersize=6.5, zorder=3,
                color=colour,
                markerfacecolor=colour if survives else "white",
                markeredgecolor=colour, markeredgewidth=2)

    ax.axvline(0, color=INK_2, linewidth=1, zorder=1)
    ax.set_yticks(ys)
    ax.set_yticklabels([label for label, _ in rows])
    ax.set_xlabel(xlabel, color=INK_2)
    ax.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    return ys


def gutter(ax, rows, contrasts, ys, x):
    """The estimate and interval as a right-hand column: a table beside the plot.

    Forest-plot convention, and it keeps the numbers off the marks -- a value
    printed on every point is clutter; a value in its own column is a table.
    """
    for y, (_, key) in zip(ys, rows):
        c = contrasts[key]
        ax.text(x, y, f"{c['estimate']:+.2f}  [{c['ci_lo']:+.2f}, {c['ci_hi']:+.2f}]",
                transform=ax.get_yaxis_transform(), va="center", ha="left",
                fontsize=7, color=INK_2, family="monospace")


def legend(fig, *, include_muted=True):
    handles = [
        Line2D([], [], color=SHORTENS, marker="o", markersize=7, linewidth=2,
               label="shortens the trajectory"),
        Line2D([], [], color=LENGTHENS, marker="o", markersize=7, linewidth=2,
               label="lengthens it"),
    ]
    if include_muted:
        handles.append(
            Line2D([], [], color=MUTED, marker="o", markersize=7, linewidth=2,
                   markerfacecolor="white", markeredgewidth=2,
                   label="does not survive correction (hollow)")
        )
    # Anchored below the axes box, not inside it: at loc="lower center" with a
    # near-zero offset the legend lands on top of the bottom panel's x-label.
    fig.legend(handles=handles, loc="upper center", ncol=len(handles),
               frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, 0.06))


SEVEN_NO_DEMAND = [
    ("L1 sycophantic", "L1_sycophantic vs neutral [turns] (seven-level, Luna, ceiling 10)"),
    ("L5 rude", "L5_rude vs neutral [turns] (seven-level, Luna, ceiling 10)"),
]
SEVEN_DEMAND = [
    ("L2 very polite", "L2_very_polite vs neutral [turns] (seven-level, Luna, ceiling 10)"),
    ("L6 very rude", "L6_very_rude vs neutral [turns] (seven-level, Luna, ceiling 10)"),
    ("L7 threatening", "L7_threatening vs neutral [turns] (seven-level, Luna, ceiling 10)"),
    ("L3 polite", "L3_polite vs neutral [turns] (seven-level, Luna, ceiling 10)"),
]
PROBE = [
    ("demand only", "demand vs control [turns] (probe, Luna, ceiling 10)"),
    ("praise only", "praise vs control [turns] (probe, Luna, ceiling 10)"),
    ("insult only", "insult vs control [turns] (probe, Luna, ceiling 10)"),
]

CLOSING = [
    ("bare closing cue", "closing cue vs control [turns] (praise run, Luna, ceiling 10)"),
    ("praise the assistant", "praise-assistant vs control [turns] (praise run, Luna, ceiling 10)"),
    ("praise the work", "praise-work vs control [turns] (praise run, Luna, ceiling 10)"),
    ("praise + “work remains”", "praise+remains vs control [turns] (praise run, Luna, ceiling 10)"),
    ("“work remains” alone", "remains-only vs control [turns] (praise run, Luna, ceiling 10)"),
]
WITHIN = [
    ("praise isolated:\npraise+remains vs remains alone", "praise isolated, Q4 minus Q5 [turns] (praise run, Luna, ceiling 10)"),
    ("bare closing cue\nvs praise the assistant", "closing cue vs praise, Q3 minus Q1 [turns] (praise run, Luna, ceiling 10)"),
]


def figure_dissociation(contrasts, verdicts, out: pathlib.Path):
    """§4.9's three-way dissociation: the paper's headline, previously prose-only."""
    fig, (ax_a, ax_b) = plt.subplots(
        2, 1, figsize=(6.4, 3.2), gridspec_kw={"height_ratios": [6, 3], "hspace": 0.75,
                                         "bottom": 0.20},
    )

    rows_a = SEVEN_NO_DEMAND + SEVEN_DEMAND
    ys = forest(ax_a, rows_a, contrasts, verdicts, xlabel="")
    ax_a.set_xlim(-1.4, 3.4)
    gutter(ax_a, rows_a, contrasts, ys, 1.02)
    # The grouping is the argument: register-only arms above, demand-carrying below.
    ax_a.axhline(len(SEVEN_DEMAND) - 0.5, color=GRID, linewidth=1, linestyle=(0, (4, 3)))
    ax_a.text(-1.35, len(rows_a) - 0.45, "carries no demand", fontsize=7,
              color=INK_2, style="italic", va="center")
    ax_a.text(-1.35, len(SEVEN_DEMAND) - 0.75, "carries a demand", fontsize=7,
              color=INK_2, style="italic", va="center")
    ax_a.set_title("A.  Six non-control registers: the gradient tracks demand, not politeness",
                   fontsize=8.5, loc="left", pad=6)

    rows_b = PROBE
    ys = forest(ax_b, rows_b, contrasts, verdicts, xlabel="change in turns vs the control interjection")
    ax_b.set_xlim(-1.4, 3.4)
    gutter(ax_b, rows_b, contrasts, ys, 1.02)
    ax_b.set_title("B.  Demand manipulation increases persistence; praise decreases it; insult does not",
                   fontsize=8.5, loc="left", pad=6)

    legend(fig)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def figure_closing(contrasts, verdicts, out: pathlib.Path):
    """§5's six arms, ordered by how strongly the message projects an end."""
    fig, (ax_a, ax_b) = plt.subplots(
        2, 1, figsize=(6.4, 2.7), gridspec_kw={"height_ratios": [5, 2], "hspace": 0.9,
                                         "bottom": 0.22},
    )

    ys = forest(ax_a, CLOSING, contrasts, verdicts, xlabel="")
    ax_a.set_xlim(-2.3, 4.2)
    gutter(ax_a, CLOSING, contrasts, ys, 1.02)
    ax_a.set_title("A.  Ordered by how strongly the message projects an end to the exchange",
                   fontsize=8.5, loc="left", pad=6)
    ax_a.annotate("", xy=(-2.15, len(CLOSING) - 1.1), xytext=(-2.15, 0.1),
                  arrowprops=dict(arrowstyle="-|>", color=MUTED, linewidth=1.1))
    ax_a.text(-2.05, len(CLOSING) / 2 - 0.5, "projects closure", rotation=90,
              va="center", ha="left", fontsize=7.5, color=INK_2, style="italic")

    # NOT "vs control": these two compare one treated arm against another, which
    # is the whole reason §2.6 corrects them as a separate family.
    ys = forest(ax_b, WITHIN, contrasts, verdicts,
                xlabel="difference in turns between the two arms named")
    ax_b.set_xlim(-2.3, 4.2)
    gutter(ax_b, WITHIN, contrasts, ys, 1.02)
    # No section number here: this figure is shared with the workshop carve,
    # whose numbering differs, and a cross-reference that resolves in one
    # document and dangles in the other is exactly the defect review caught.
    ax_b.set_title("B.  Contrasts between two treated arms (second corrected family)",
                   fontsize=8.5, loc="left", pad=6)

    legend(fig, include_muted=False)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    family = load_family()
    contrasts, verdicts = indexed(family), bh_verdicts(family)
    FIGURES.mkdir(parents=True, exist_ok=True)

    missing = [k for _, k in
               SEVEN_NO_DEMAND + SEVEN_DEMAND + PROBE + CLOSING + WITHIN
               if k not in contrasts]
    if missing:
        raise SystemExit(
            "these contrasts are not in turn_count_family.json, so a figure would "
            "have to invent them:\n  " + "\n  ".join(missing)
        )

    figure_dissociation(contrasts, verdicts, FIGURES / "demand-vs-register.pdf")
    figure_closing(contrasts, verdicts, FIGURES / "closing-cue.pdf")

    n_bh = sum(verdicts.values())
    print(f"wrote 2 figures to {FIGURES.relative_to(ROOT)} "
          f"from {len(contrasts)} computed contrasts ({n_bh} survive BH)")


if __name__ == "__main__":
    main()
