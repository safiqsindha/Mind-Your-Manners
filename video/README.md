# Explainer video

A 1 min 55 s explainer of the v1.0 paper in the 3Blue1Brown style, made with
[Manim Community](https://www.manim.community/). Every number on screen is quoted from the paper,
and all effects in steps are GPT-5.6 Luna, as in the paper.

| File | What it is |
|---|---|
| `mind-your-manners-explainer.mp4` | The video: 1920×1080, 60 fps, captions burned in, no narration |
| `transcript.md` | Full transcript plus a description of every animation |
| `captions.srt` | The on-screen captions as a sidecar file, for platforms that want one (they are already burned in, so uploading both shows them twice) |
| `explainer.py` | The Manim source |
| `thumbnail.jpg` | Poster frame with a play button, used in the main README |

The video is also on the [project page](https://safiqsindha.github.io/Mind-Your-Manners/#watch).

## Re-rendering

```bash
pip install manim==0.22.0          # needs cairo, pango, ffmpeg
# LaTeX (for the numbers) and the Latin Modern fonts: texlive-latex-extra, dvisvgm, lmodern
manim -qh explainer.py Short       # ~2 min on a laptop
```

**Accessibility**

- Every text colour is at least 7:1 on the background.
- Direction is shown by shape as well as colour: ▲ more steps, ▼ fewer steps, ● no change.
- Captions are held for roughly 3.3 words per second.
