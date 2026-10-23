# Explainer video: transcript and description

For screen readers and anyone who can't watch the video. Every number is from the v1.0 paper.

## The question

Two speech bubbles: a polite one ("Would you kindly keep going?") and a rude one ("Hurry up and keep going.").

Does tone change what an AI agent does?

## How we tested

Diagram: an AI agent and a spreadsheet task, with arrows showing it runs code and sees the result. A dot travels the loop while a counter ticks up: step 1, 2, 3.

An AI agent worked on 50 real spreadsheet tasks, one step at a time. A step is one round of writing and running code.

Partway through, we slipped one short note into what it saw.

Four rows of 28 squares show that every note was exactly 28 tokens and started with the same first words. Only the words after that changed.

9,850 test runs · 2 AI models · 50 tasks.

## Result 1

On a number line of extra steps compared with a plain note, the "very polite" and "very rude" bubbles each collapse into a point and slide out to their values:

- Very polite: +0.70 steps.
- Very rude: +0.71 steps.
Very polite and very rude notes added almost exactly the same number of steps.

- "Please continue": +1.17 steps.
- An insult with no request: −0.08 steps.
What mattered was asking it to keep going. An insult with no request did nothing measurable.

Asking moved the agent. Tone didn't.

## Result 2

- A note saying work remains: +1.85 steps.
- The same note with praise added slides back to +0.50 steps.
Adding praise to that same note made the agent stop sooner, even though it said work was left.

- "No more notes will follow": −1.44 steps (measured in one run).
A note saying no more notes would follow made it stop soonest.

## Result 3

Six step blocks: the extra steps 5 and 6 are marked "changed nothing", and a star over step 2 marks the best answer.

Most extra steps changed nothing. The agent's first answer was usually already its best.

On a number line of change in right answers, a green band from −4 to +4 percentage points reads "no reliable change".

None of the notes reliably changed how often it got the right answer.

## What it means

Tone doesn't steer an AI agent. Asking does.

+0.70 / +0.71 — Be clear, not polite.

−0.59 / −1.44 — Don't praise it mid-task.

+1.17 — Count steps, not just right answers.

Sindha, 2026 · GPT-5.6 Luna · 50 tasks · 9,850 test runs

safiqsindha.github.io/Mind-Your-Manners

