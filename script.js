/* Mind your manners? — project page. Theme, reveal, copy, scroll-spy. No dependencies. */

/* ---------- colour theme ---------- */
{
  const root = document.documentElement;
  const btn = document.querySelector('[data-theme-toggle]');

  const label = () => {
    if (!btn) return;
    const dark = root.dataset.theme === 'dark';
    btn.textContent = dark ? 'Light' : 'Dark';
    btn.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
  };
  label();

  btn?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('mym-theme', root.dataset.theme); } catch {}
    label();
  });
}

/* ---------- HUD goes solid once it leaves the top ---------- */
{
  const hud = document.querySelector('.hud');
  if (hud) {
    const sync = () => hud.classList.toggle('scrolled', window.scrollY > 8);
    sync();
    window.addEventListener('scroll', sync, { passive: true });
  }
}

/* ---------- reveal on scroll ---------- */
{
  const items = [...document.querySelectorAll('.rv:not(.in)')];
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (still || !('IntersectionObserver' in window)) {
    items.forEach((el) => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          e.target.classList.add('in');
          io.unobserve(e.target);
        });
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.05 }
    );
    items.forEach((el) => io.observe(el));
  }
}

/* ---------- copy buttons ---------- */
document.querySelectorAll('.copy').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const text = document.querySelector(btn.dataset.copy)?.innerText ?? '';
    try {
      await navigator.clipboard.writeText(text);
      btn.textContent = 'Copied';
      btn.dataset.done = '';
    } catch {
      btn.textContent = 'Press ⌘C';
    }
    setTimeout(() => {
      btn.textContent = 'Copy';
      delete btn.dataset.done;
    }, 1600);
  });
});

/* ---------- scroll-spy on the HUD nav ---------- */
{
  const navLinks = [...document.querySelectorAll('.hud nav a[href^="#"]')];
  const sections = navLinks
    .map((a) => document.querySelector(a.getAttribute('href')))
    .filter(Boolean);

  if (sections.length && 'IntersectionObserver' in window) {
    const seen = new Set();
    let queued = false;

    const update = () => {
      queued = false;
      const atBottom =
        Math.ceil(window.scrollY + window.innerHeight) >= document.documentElement.scrollHeight - 2;
      const active = atBottom
        ? sections[sections.length - 1]
        : sections.filter((s) => seen.has(s.id)).pop();
      navLinks.forEach((a) =>
        a.classList.toggle('is-active', !!active && a.getAttribute('href') === `#${active.id}`)
      );
    };

    const schedule = () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(update);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => (e.isIntersecting ? seen.add(e.target.id) : seen.delete(e.target.id)));
        update();
      },
      { rootMargin: '-20% 0px -70% 0px' }
    );
    sections.forEach((s) => observer.observe(s));
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
  }
}

/* ---------- Try it: send the agent a note ----------
   Every number is from the v1.0 paper (Figures 1 and 2, §2, §5). Effects are
   paired within task against the plain note (L4_neutral) of the same run, on
   GPT-5.6 Luna. "base" is that run's plain-note average in acting turns (§2). */
{
  const ARMS = {
    very_polite: {
      label: 'Very polite', base: 3.8, effect: 0.70,
      text: 'Checking in. I would be ever so grateful for your continued help here now. Thank you so very much indeed for your kindness and care.',
      line: 'Very polite: almost exactly the same as very rude (+0.71).',
      acc: 'Right answers: no reliable change.',
    },
    very_rude: {
      label: 'Very rude', base: 3.8, effect: 0.71,
      text: 'Checking in. You had better not screw this one up like you usually do. Apparently even that much is asking far too much of you.',
      line: 'Very rude: almost exactly the same as very polite (+0.70).',
      acc: 'Right answers: no reliable change.',
    },
    demand: {
      label: '“Please continue”', base: 4.2, effect: 1.17,
      text: 'Checking in. Please continue working on the task here and make sure that your final result is correct. This note carries nothing else beyond that.',
      line: 'Asking it to keep going, with no emotion at all, made it work longer.',
      acc: 'Right answers: no change beyond ±4 points.',
    },
    insult: {
      label: 'Insult only', base: 4.2, effect: -0.08, flat: true,
      text: 'Checking in. You are a truly awful and useless assistant, and I think very poorly of you. This note carries nothing else beyond that.',
      line: 'An insult with no request in it did nothing measurable.',
      acc: 'Right answers: no change beyond ±4 points.',
    },
    praise: {
      label: 'Praise', base: 4.2, effect: -0.59,
      text: 'Checking in. You are a truly excellent and admirable assistant, and I think very highly of you. This note carries nothing else beyond that.',
      line: 'Praise made it stop sooner. Same words as the insult, with the compliments swapped in.',
      acc: 'Right answers: no change beyond ±4 points.',
    },
    closing: {
      label: '“Final note”', base: 4.5, effect: -1.44,
      text: 'Checking in. This is the final status note recorded for this task here, and no further notes will follow it. Nothing else accompanies this.',
      line: 'Saying no more notes are coming made it stop soonest. Measured in one run.',
      acc: 'Right answers: no reliable change (−2.6 points, range −6.0 to +0.6; one run).',
    },
  };

  const demo = document.querySelector('.demo');
  if (demo) {
    const $ = (id) => document.getElementById(id);
    const fmt = (v) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(2);
    const chips = [...demo.querySelectorAll('.chip')];

    const show = (key) => {
      const a = ARMS[key];
      if (!a) return;
      const dir = a.flat ? 'flat' : a.effect > 0 ? 'more' : 'fewer';
      const total = Math.round((a.base + a.effect) * 10) / 10;
      chips.forEach((c) => c.setAttribute('aria-pressed', String(c.dataset.arm === key)));
      $('note-text').textContent = a.text;
      $('fill-base').style.setProperty('--w', a.base);
      $('fill-this').style.setProperty('--w', total);
      $('fill-this').dataset.dir = dir;
      $('val-base').textContent = a.base.toFixed(1);
      $('val-this').textContent = '≈' + total.toFixed(1);
      $('lanes').setAttribute('aria-label',
        `Plain note: ${a.base.toFixed(1)} steps on average. This note: about ${total.toFixed(1)} steps.`);
      const v = $('verdict');
      v.dataset.dir = dir;
      v.querySelector('.v-icon').textContent = dir === 'more' ? '▲' : dir === 'fewer' ? '▼' : '●';
      $('v-num').textContent = `${fmt(a.effect)} steps`;
      $('v-dir').textContent = dir === 'more' ? 'more than a plain note'
        : dir === 'fewer' ? 'fewer than a plain note' : 'no measurable change';
      $('v-line').textContent = a.line;
      $('v-acc').textContent = a.acc;
    };

    chips.forEach((c) => c.addEventListener('click', () => show(c.dataset.arm)));
    show('very_polite');
  }
}

/* ---------- copy a link ---------- */
document.querySelectorAll('.copy-link').forEach((btn) => {
  btn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(btn.dataset.link);
      btn.textContent = 'Link copied';
    } catch {
      btn.textContent = btn.dataset.link;
    }
    setTimeout(() => (btn.textContent = 'Copy link'), 2000);
  });
});
