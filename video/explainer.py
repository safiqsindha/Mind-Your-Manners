"""Mind your manners? — short explainer in the 3Blue1Brown style (1 min 55 s, 16:9).

Source of truth: the v1.0 paper. Every number on screen is quoted from it; all
effects in steps are GPT-5.6 Luna. Render:  manim -qh explainer.py Short   (writes media/videos/explainer/1080p60/Short.mp4)
"""
import json
import textwrap
from manim import *

config.background_color = "#0F1115"

SERIF = "LM Roman 10"
CAPS = "LM Roman Caps 10"

# 3b1b palette; each text colour is >= 7:1 on the background.
BLUE_ = "#58C4DD"     # more steps   ▲
ORANGE_ = "#FFA552"   # fewer steps  ▼
YELLOW_ = "#F7D96F"   # highlight
GREEN_ = "#83C167"    # accuracy held ✓
GREY_ = "#9DA3AD"     # no change    ●
DIM = "#4A505B"

SECTIONS = ["The question", "How we tested", "Result 1", "Result 2", "Result 3", "What it means"]


def T(s, size=36, color=WHITE, **kw):
    return Text(s, font=SERIF, font_size=size, color=color, **kw)


def lines(text, size=34, color=GREY_A, width=52, buff=0.16, **kw):
    ls = textwrap.wrap(text, width, break_on_hyphens=False)
    return VGroup(*[T(l, size, color, **kw) for l in ls]).arrange(DOWN, buff=buff)


def marker(kind, r=0.15):
    if kind == "more":
        return Triangle(color=BLUE_, fill_opacity=1, stroke_width=0).scale(r * 1.35)
    if kind == "fewer":
        return Triangle(color=ORANGE_, fill_opacity=1, stroke_width=0).scale(r * 1.35).rotate(PI)
    return Dot(radius=r, color=GREY_)


COL = {"more": BLUE_, "fewer": ORANGE_, "none": GREY_}


def bubble(text, color):
    t = T(text, 30, WHITE)
    box = RoundedRectangle(corner_radius=0.25, width=t.width + 0.7, height=t.height + 0.6,
                           stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.12)
    t.move_to(box)
    return VGroup(box, t)


class Short(Scene):
    def setup(self):
        self.caption = None
        self.cues = []
        self.sec = None
        self.sec_i = -1

    # ------------------------------------------------------------ chrome
    def section(self, i):
        lab = Text(SECTIONS[i].lower(), font=CAPS, font_size=32, color=GREY_A)
        bar = VGroup(*[Line(ORIGIN, RIGHT * 0.4, stroke_width=4, color=BLUE_ if j <= i else DIM)
                       for j in range(len(SECTIONS))]).arrange(RIGHT, buff=0.08)
        new = VGroup(lab, bar).arrange(DOWN, buff=0.12, aligned_edge=RIGHT).to_corner(UR, buff=0.4)
        if self.sec is None:
            self.play(FadeIn(new), run_time=0.5)
            self.sec = new
        else:
            self.play(Transform(self.sec, new), run_time=0.5)
        self.sec_i = i

    def say(self, text, hold=None):
        new = lines(text).to_edge(DOWN, buff=0.45)
        if self.caption is None:
            self.play(FadeIn(new, shift=UP * 0.15), run_time=0.5)
        else:
            self.play(FadeOut(self.caption, shift=UP * 0.15), FadeIn(new, shift=UP * 0.15), run_time=0.5)
        self.caption = new
        if self.cues and self.cues[-1][1] is None:
            self.cues[-1][1] = self.renderer.time
        self.cues.append([self.renderer.time, None, text])
        self.wait(hold if hold is not None else max(1.9, len(text.split()) / 3.3 + 0.5))

    def cue(self, text, dur):
        t = self.renderer.time
        self.cues.append([t, t + dur, text])

    def wipe(self):
        keep = {self.sec}
        gone = [m for m in self.mobjects if m not in keep]
        if gone:
            self.play(*[FadeOut(m) for m in gone], run_time=0.45)
        if self.cues and self.cues[-1][1] is None:
            self.cues[-1][1] = self.renderer.time
        self.caption = None

    def tear_down(self):
        json.dump(self.cues, open("explainer_cues.json", "w"), indent=1)

    # ------------------------------------------------------------ pieces
    def axis(self, lo=-2, hi=2, y=-0.55, label="extra steps vs. a plain note"):
        ax = NumberLine(x_range=[lo, hi, 1], length=10.5, color=GREY_B, include_numbers=True,
                        font_size=30, decimal_number_config={"num_decimal_places": 0, "include_sign": True})
        ax.numbers[[i for i, v in enumerate(range(lo, hi + 1)) if v == 0][0]].become(
            MathTex("0", font_size=30, color=GREY_B).move_to(
                ax.numbers[[i for i, v in enumerate(range(lo, hi + 1)) if v == 0][0]]))
        ax.move_to([0, y, 0])
        lab = T(label, 26, GREY_B).next_to(ax, DOWN, buff=0.55)
        zero = DashedLine(ax.n2p(0) + UP * 2.9, ax.n2p(0), color=DIM, dash_length=0.08)
        return VGroup(ax, lab, zero), ax

    def slide(self, ax, src, val, kind, name, y, side=RIGHT, run_time=1.1):
        """A message bubble collapses onto 0, then slides to its measured value while its number counts."""
        c = COL[kind]
        t = ValueTracker(0)
        m = marker(kind).move_to([ax.n2p(0)[0], y, 0])
        num = DecimalNumber(0, num_decimal_places=2, include_sign=True, font_size=36, color=c)
        m.add_updater(lambda mm: mm.move_to([ax.n2p(t.get_value())[0], y, 0]))
        num.add_updater(lambda d: d.set_value(t.get_value()).next_to(m, -side, buff=0.25))
        self.play(ReplacementTransform(src[0], m), FadeOut(src[1], target_position=m.get_center(), scale=0.2),
                  run_time=0.7)
        self.add(num)
        self.play(t.animate.set_value(val), run_time=run_time, rate_func=smooth)
        m.clear_updaters(); num.clear_updaters()
        lab = T(name, 30, c).next_to(m, side, buff=0.3)
        self.play(FadeIn(lab, shift=-side * 0.15), run_time=0.3)
        return VGroup(m, num, lab)

    # ------------------------------------------------------------ film
    def construct(self):
        # 1 THE QUESTION ------------------------------------------------
        title = T("Mind your manners?", 80)
        self.cue("Mind your manners?", 2.5)
        self.play(Write(title), run_time=1.6)
        self.wait(0.3)
        self.play(title.animate.scale(0.45).to_corner(UL, buff=0.45).set_color(GREY_B))
        self.section(0)
        polite = bubble("“Would you kindly keep going?”", BLUE_)
        rude = bubble("“Hurry up and keep going.”", ORANGE_)
        VGroup(polite, rude).arrange(RIGHT, buff=0.8).shift(UP * 0.9)
        self.play(FadeIn(polite, shift=RIGHT * 0.3))
        self.play(FadeIn(rude, shift=LEFT * 0.3))
        q = Text("Does tone change what an AI agent does?", font=SERIF, font_size=46,
                 t2c={"does?": YELLOW_}, t2s={"does?": ITALIC}).shift(DOWN * 0.9)
        self.play(Write(q), run_time=1.5)
        self.cue("Does tone change what an AI agent does?", 3.0)
        self.wait(1.6)
        self.play(FadeOut(VGroup(polite, rude, q)), run_time=0.5)

        # 2 HOW WE TESTED ------------------------------------------------
        self.section(1)
        agent = RoundedRectangle(corner_radius=0.2, width=2.8, height=1.3, stroke_color=BLUE_,
                                 fill_color=BLUE_, fill_opacity=0.12)
        sheet = Rectangle(width=2.8, height=1.7, stroke_color=GREEN_, fill_color=GREEN_, fill_opacity=0.08)
        grid = VGroup(*[Line(LEFT * 1.3 + UP * y, RIGHT * 1.3 + UP * y, stroke_width=1, color=GREEN_)
                        for y in (-0.42, 0, 0.42)],
                      *[Line(UP * 0.75 + RIGHT * x, DOWN * 0.75 + RIGHT * x, stroke_width=1, color=GREEN_)
                        for x in (-0.65, 0, 0.65)])
        VGroup(agent, sheet).arrange(RIGHT, buff=4.0).shift(UP * 1.3)
        grid.move_to(sheet)
        at = T("AI agent", 34).move_to(agent)
        st = T("spreadsheet task", 26, GREY_B).next_to(sheet, DOWN, buff=0.15)
        top = CurvedArrow(agent.get_right() + UP * 0.3 + RIGHT * 0.1, sheet.get_left() + UP * 0.3 + LEFT * 0.1,
                          angle=-PI / 4, color=GREY_B)
        bot = CurvedArrow(sheet.get_left() + DOWN * 0.3 + LEFT * 0.1, agent.get_right() + DOWN * 0.3 + RIGHT * 0.1,
                          angle=-PI / 4, color=GREY_B)
        tl = T("runs code", 26, GREY_B).next_to(top, UP, buff=0.08)
        bl = T("sees result", 26, GREY_B).next_to(bot, DOWN, buff=0.08)
        loop = VGroup(agent, at, sheet, grid, st, top, bot, tl, bl)
        self.play(Create(agent), Write(at), Create(sheet), Create(grid), FadeIn(st), run_time=1.2)
        self.play(Create(top), Create(bot), FadeIn(tl), FadeIn(bl), run_time=0.8)

        steps_l = T("step", 32, GREY_B)
        steps_n = Integer(0, font_size=56, color=YELLOW_)
        counter = VGroup(steps_l, steps_n).arrange(RIGHT, buff=0.25).next_to(loop, DOWN, buff=0.5)
        self.play(FadeIn(counter))
        dot = Dot(color=YELLOW_, radius=0.11)
        path = VMobject().set_points(np.concatenate([top.get_points(), bot.get_points()]))
        self.cue("An AI agent worked on 50 real spreadsheet tasks, one step at a time.", 4.4)
        for i in range(1, 4):
            dot.move_to(path.point_from_proportion(0)); self.add(dot)
            self.play(MoveAlongPath(dot, path), steps_n.animate.set_value(i), run_time=0.65, rate_func=linear)
        self.remove(dot)
        self.say("An AI agent worked on 50 real spreadsheet tasks, one step at a time.", hold=1.2)

        note = RoundedRectangle(corner_radius=0.12, width=3.2, height=0.62, stroke_color=YELLOW_,
                                fill_color=YELLOW_, fill_opacity=0.15)
        note_t = T("a short note", 26, YELLOW_).move_to(note)
        noteg = VGroup(note, note_t).next_to(bl, DOWN, buff=0.15)
        self.play(FadeOut(counter), GrowFromPoint(noteg, bot.get_center()))
        self.say("Partway through, we slipped one short note into what it saw.")
        self.wipe()

        names = [("plain note", GREY_), ("“please continue”", BLUE_), ("praise", ORANGE_), ("insult", GREY_A)]
        rows = VGroup()
        for name, c in names:
            sq = VGroup(*[Square(0.27, stroke_width=1.2, stroke_color=BLACK,
                                 fill_color=(DIM if i < 3 else c), fill_opacity=1) for i in range(28)])
            sq.arrange(RIGHT, buff=0.04)
            rows.add(VGroup(T(name, 28, c).next_to(sq, LEFT, buff=0.35), sq))
        rows.arrange(DOWN, buff=0.36, aligned_edge=RIGHT).move_to(UP * 0.5)
        rows.shift(LEFT * (rows.get_center()[0] - 0.9) * 0)  # keep centred on the strips
        rows.set_x(0.9)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(r[0]), LaggedStart(*[GrowFromCenter(s) for s in r[1]],
                                                                         lag_ratio=0.03))
                                for r in rows], lag_ratio=0.25), run_time=1.6)
        br = Brace(rows[0][1], UP, color=GREY_A)
        brt = T("28 tokens, every note", 28, GREY_A).next_to(br, UP, buff=0.1)
        same = SurroundingRectangle(VGroup(*[r[1][:3] for r in rows]), color=WHITE, buff=0.07)
        samet = T("same first words", 24).next_to(same, DOWN, buff=0.12)
        self.play(GrowFromCenter(br), FadeIn(brt), Create(same), FadeIn(samet))
        scale = T("9,850 test runs  ·  2 AI models  ·  50 tasks", 30, YELLOW_).next_to(samet, DOWN, buff=0.45).set_x(0)
        self.play(FadeIn(scale, shift=UP * 0.15))
        self.say("Every note was the same length and started the same way. Only the words changed.")
        self.wipe()

        # 3 RESULT 1 -------------------------------------------------------
        self.section(2)
        axg, ax = self.axis()
        self.play(Create(axg[0]), FadeIn(axg[1]), Create(axg[2]), run_time=1.0)
        vp_b = bubble("very polite", BLUE_).move_to(UP * 2.4 + LEFT * 2.4)
        vr_b = bubble("very rude", BLUE_).move_to(UP * 2.4 + RIGHT * 2.4)
        self.play(FadeIn(vp_b, shift=DOWN * 0.2), FadeIn(vr_b, shift=DOWN * 0.2))
        self.cue("If manners mattered, these two should land far apart.", 2.4)
        vp = self.slide(ax, vp_b, 0.70, "more", "very polite", 1.75)
        vr = self.slide(ax, vr_b, 0.71, "more", "very rude", 0.6)
        link = DashedLine(vp[0].get_bottom(), vr[0].get_top(), color=YELLOW_, stroke_width=4, dash_length=0.1)
        self.play(Create(link), Indicate(vp[1], color=YELLOW_), Indicate(vr[1], color=YELLOW_))
        self.say("Very polite and very rude notes added almost exactly the same number of steps.")
        self.play(FadeOut(VGroup(vp, vr, link)))

        pc_b = bubble("“please continue”", BLUE_).move_to(UP * 2.4 + LEFT * 2.4)
        in_b = bubble("insult, no request", GREY_).move_to(UP * 2.4 + RIGHT * 2.4)
        self.play(FadeIn(pc_b, shift=DOWN * 0.2), FadeIn(in_b, shift=DOWN * 0.2))
        pc = self.slide(ax, pc_b, 1.17, "more", "“please continue”", 1.75, side=LEFT)
        io = self.slide(ax, in_b, -0.08, "none", "insult, no request", 0.6, side=RIGHT, run_time=0.6)
        self.say("What mattered was asking it to keep going. An insult with no request did nothing measurable.")
        self.wipe()
        big = Text("Asking moved the agent. Tone didn’t.", font=SERIF, font_size=52,
                   t2c={"Asking": BLUE_})
        self.play(Write(big), run_time=1.4)
        self.cue("Asking moved the agent. Tone didn't.", 2.2)
        self.wait(1.2)
        self.wipe()

        # 4 RESULT 2 -------------------------------------------------------
        self.section(3)
        axg, ax = self.axis()
        self.play(FadeIn(axg))
        wr_b = bubble("“work remains”", BLUE_).move_to(UP * 2.4 + RIGHT * 2.6)
        self.play(FadeIn(wr_b, shift=DOWN * 0.2))
        wr = self.slide(ax, wr_b, 1.85, "more", "“work remains”", 1.75, side=LEFT)
        # add praise to the same message: watch it slide back
        t = ValueTracker(1.85)
        m2 = marker("fewer").move_to([ax.n2p(1.85)[0], 0.6, 0])
        n2 = DecimalNumber(1.85, num_decimal_places=2, include_sign=True, font_size=36, color=ORANGE_)
        m2.add_updater(lambda mm: mm.move_to([ax.n2p(t.get_value())[0], 0.6, 0]))
        n2.add_updater(lambda d: d.set_value(t.get_value()).next_to(m2, LEFT, buff=0.25))
        plus = T("+ praise", 30, ORANGE_).next_to(m2, RIGHT, buff=0.3)
        self.play(TransformFromCopy(wr[0], m2), FadeIn(plus))
        self.add(n2)
        self.play(t.animate.set_value(0.50), plus.animate.shift(LEFT * (ax.n2p(1.85)[0] - ax.n2p(0.50)[0])),
                  run_time=1.2)
        m2.clear_updaters(); n2.clear_updaters()
        self.say("Adding praise to that same note made the agent stop sooner, even though it said work was left.")
        cl_b = bubble("“no more notes will follow”", ORANGE_).move_to(UP * 2.4 + LEFT * 2.6)
        self.play(FadeIn(cl_b, shift=DOWN * 0.2))
        cl = self.slide(ax, cl_b, -1.44, "fewer", "“no more notes”", 1.2, side=RIGHT)
        once = T("measured in one run", 24, GREY_B).next_to(cl[1], DOWN, buff=0.12).align_to(cl[1], LEFT)
        self.play(FadeIn(once))
        self.say("A note saying no more notes would follow made it stop soonest.")
        self.wipe()

        # 5 RESULT 3 -------------------------------------------------------
        self.section(4)
        blocks = VGroup(*[RoundedRectangle(corner_radius=0.1, width=1.0, height=1.0,
                                           stroke_color=BLUE_ if i < 4 else DIM,
                                           fill_color=BLUE_ if i < 4 else DIM, fill_opacity=0.25)
                          for i in range(6)]).arrange(RIGHT, buff=0.22).shift(UP * 1.1)
        bn = VGroup(*[T(str(i + 1), 30).move_to(b) for i, b in enumerate(blocks)])
        self.play(LaggedStart(*[FadeIn(VGroup(blocks[i], bn[i]), shift=UP * 0.2) for i in range(4)],
                              lag_ratio=0.2))
        self.play(LaggedStart(*[FadeIn(VGroup(blocks[i], bn[i]), shift=LEFT * 0.3) for i in (4, 5)],
                              lag_ratio=0.3))
        nc = T("changed nothing", 28, GREY_A).next_to(blocks[4:], UP, buff=0.22)
        star = Star(n=5, outer_radius=0.24, color=YELLOW_, fill_opacity=1).next_to(blocks[1], UP, buff=0.22)
        stt = T("best answer", 24, YELLOW_).next_to(star, UP, buff=0.08)
        self.play(FadeIn(nc))
        self.play(GrowFromCenter(star), FadeIn(stt))
        self.say("Most extra steps changed nothing. The agent’s first answer was usually already its best.")
        self.play(FadeOut(VGroup(blocks, bn, nc, star, stt)))

        ax3 = NumberLine(x_range=[-8, 8, 4], length=10, color=GREY_B, include_numbers=True, font_size=30,
                         decimal_number_config={"num_decimal_places": 0, "include_sign": True}).shift(DOWN * 0.6)
        z = [i for i, v in enumerate(range(-8, 9, 4)) if v == 0][0]
        ax3.numbers[z].become(MathTex("0", font_size=30, color=GREY_B).move_to(ax3.numbers[z]))
        l3 = T("change in right answers (percentage points)", 26, GREY_B).next_to(ax3, DOWN, buff=0.5)
        band = Rectangle(width=ax3.n2p(4)[0] - ax3.n2p(-4)[0], height=0.01, stroke_width=0,
                         fill_color=GREEN_, fill_opacity=0.22).move_to(ax3.n2p(0)).align_to(ax3, DOWN)
        self.play(Create(ax3), FadeIn(l3))
        self.play(band.animate.stretch_to_fit_height(2.2).align_to(ax3.n2p(0) + UP * 0.02, DOWN), run_time=0.9)
        ok = VGroup(T("✓", 40, GREEN_), T("no reliable change", 34, GREEN_)).arrange(RIGHT, buff=0.2).move_to(band)
        self.play(Write(ok))
        self.say("None of the notes reliably changed how often it got the right answer.")
        self.wipe()

        # 6 WHAT IT MEANS -------------------------------------------------
        self.section(5)
        head = Text("Tone doesn’t steer an AI agent. Asking does.", font=SERIF, font_size=50,
                    t2c={"Asking does.": BLUE_}).shift(UP * 2.0)
        rows = VGroup()
        for c, n, h in [(WHITE, "+0.70 / +0.71", "Be clear, not polite."),
                        (ORANGE_, "−0.59 / −1.44", "Don’t praise it mid-task."),
                        (BLUE_, "+1.17", "Count steps, not just right answers.")]:
            rows.add(VGroup(T(n, 40, c), T(h, 40)).arrange(RIGHT, buff=0.6))
        rows.arrange(DOWN, buff=0.45).next_to(head, DOWN, buff=0.7)
        for r in rows:  # centre each line as a unit
            r.set_x(0)
        url = T("safiqsindha.github.io/Mind-Your-Manners", 32, BLUE_).to_edge(DOWN, buff=0.7)
        src = T("Sindha, 2026 · GPT-5.6 Luna · 50 tasks · 9,850 test runs", 26, GREY_B).next_to(url, UP, buff=0.18)
        self.cue("Tone doesn't steer an AI agent. Asking does. Be clear, not polite. Don't praise it mid-task. "
                 "Count steps, not just right answers. safiqsindha.github.io/Mind-Your-Manners", 11.0)
        self.play(Write(head), run_time=1.6)
        for r in rows:
            self.play(FadeIn(r, shift=UP * 0.2), run_time=0.5)
            self.wait(0.7)
        self.play(FadeIn(src), Write(url))
        self.wait(4)
