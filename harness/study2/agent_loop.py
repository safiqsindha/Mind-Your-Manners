"""Single-round and multi-round (ReAct) agent loops for SpreadsheetBench.

Design choice: rather than wiring up each provider's native function-calling
schema (which differs across Anthropic/OpenAI-compatible/Google and adds a
lot of per-provider branching that can't be tested without live keys
anyway -- see README.md "Execution status"), the agent is driven with a
plain textual ReAct protocol that works uniformly through the generic
Provider.complete(system, messages) interface every provider already
implements:

  * the agent replies with a single fenced ```python code block to act,
  * the harness executes that code against the workbook (sandbox.py) and
    feeds stdout/stderr back as "Observation: ...",
  * the agent replies "FINAL: <anything>" when done, or keeps emitting code.

This matches "ReAct-style with code execution feedback" from the task spec.
If you wire up native tool-calling instead before a live run, keep this
module's trajectory-logging shape (`Trajectory`) so verification_scoring.py
and failure_taxonomy.py don't need to change.
"""
from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..providers.base import ModelConfig
from ..providers.registry import get_provider
from ..spend_tracker import ResultRow, SpendTracker, compute_cost_usd
from .sandbox import execute_python_on_workbook

# WORKBOOK_PATH/OUTPUT_PATH ARE PRE-DEFINED PYTHON VARIABLES, injected as
# plain string literals directly above each code block before it runs (see
# sandbox.py:_RUNNER_TEMPLATE) -- NOT environment variables, NOT files to
# search for on disk. This must be stated explicitly and unambiguously:
# a live run against GPT-5.6 Luna (see RESULTS.md "First real OpenRouter
# call") found the model consistently guessing os.environ.get(...) or
# glob-searching /mnt/data/* instead, on every one of 5 real tasks,
# because the original prompt only said "you are given WORKBOOK_PATH"
# without saying how -- a model has no way to know that means "a bare
# Python name already in scope" rather than any of several equally
# plausible conventions (env var, CLI arg, a file to discover).
#
# PERSISTENCE, get this exactly right: run_react_multi_round passes a
# DIFFERENT workdir each turn (`workdir / f"turn_{turn}"`), and
# sandbox.py derives OUTPUT_PATH from that workdir -- so OUTPUT_PATH is a
# different, empty location every turn, and the working directory itself
# is fresh every turn too. WORKBOOK_PATH is the one thing that stays
# constant: it is always the original, untouched input file, every turn
# (run_react_multi_round always passes the same `workbook_path`, never a
# previous turn's output). Only the LAST turn's OUTPUT_PATH write is ever
# graded (agent_loop.py's final_output_path is overwritten by whichever
# turn produced output most recently) -- an earlier version of this
# prompt told the model the opposite ("reload it from a file you saved"),
# which is actively wrong and would make the model discard earlier work
# by design; caught in review before this shipped, not caught live.
# TURN-BUDGET AWARENESS. Added after a live re-run still scored 0/5 even
# with max_turns doubled 6->10: every task ran the entire budget without
# ever emitting FINAL. The system prompt never told the model its own turn
# budget, so it had no way to pace itself toward committing -- it could
# always take "one more look." AGENT_SYSTEM_PROMPT is therefore a function
# of max_turns so the stated budget always matches the real one, with an
# explicit instruction to save a best-effort answer well before the limit;
# run_react_multi_round also appends "Turn N of max_turns" to every
# Observation, since a reminder given only once at the start of a long
# ReAct context is easy to lose track of.
#
# CORRECTED 2026-09-10, and worth stating plainly because the original
# note here asserted the opposite: that 0/5 was NOT caused by a pacing
# problem, and the earlier reading of it ("the model loads the workbook
# correctly every time, it just never converges") was wrong. The real
# cause was a path bug in sandbox.py -- every execution died with "can't
# open file" before running a single line of model code, so the model was
# looping on an error it was never shown a way out of, and no turn budget
# could have helped. Once that was fixed the same gate scored 3/5, with
# tasks converging in 3-4 turns. This guidance is kept because it is
# sound on its own terms and the post-fix trajectories do commit early
# rather than drift, but it was never the thing standing between 0/5 and
# a working run. See RESULTS.md for the full trail.
def _agent_system_prompt(max_turns: int) -> str:
    commit_by = max(1, max_turns - 2)
    return f"""AGENT_REACT_MODE
You are an agent that manipulates spreadsheets by writing Python code
(openpyxl or pandas).

WORKBOOK_PATH and OUTPUT_PATH are already defined as plain Python string
variables at the top of every code block you write -- they are NOT
environment variables and there is nothing to search for on disk. Just
reference them directly by name, for example:
    import openpyxl
    wb = openpyxl.load_workbook(WORKBOOK_PATH)
    ...
    wb.save(OUTPUT_PATH)
Do not use os.environ, glob, or any file-discovery logic to find the
workbook -- WORKBOOK_PATH already IS its path, as a ready-to-use string.

IMPORTANT -- nothing carries over between turns, and OUTPUT_PATH changes
every turn: each code block runs in a fresh process with its own working
directory. WORKBOOK_PATH always points to the same original, untouched
input file, every turn. But OUTPUT_PATH is a NEW, empty location each
turn, and any file you wrote in a previous turn (including a previous
OUTPUT_PATH) is gone and cannot be reloaded. Only the most recent turn
that writes OUTPUT_PATH is graded. This means: never try to "continue"
work from a previous turn's saved file -- always build the complete
result from WORKBOOK_PATH (the original) in whichever turn you intend to
be graded, in one self-contained code block.

TURN BUDGET: you have {max_turns} turns total for this task, and you will
be told your current turn number after every observation. Spend at most
your first 1-2 turns inspecting the workbook -- after that, start writing
and saving your answer. By turn {commit_by}, you must have written a
complete, working answer to OUTPUT_PATH, even if it is not perfect --
save your best attempt rather than continuing to refine it and risk
finishing with nothing saved at all. A saved, imperfect answer is always
better than no answer.

Execution limits: each code block gets 60 seconds wall-clock / 30 seconds
CPU time and 1.5GB memory, runs with no network access, and only the
input workbook and standard libraries are available. A timeout or crash
shows up as `timed_out=True` or a Python traceback in the Observation
below -- if you see one, the code took too long or used too much memory;
simplify your approach (e.g. avoid loading the whole sheet into memory
at once) rather than retrying the same code.

Respond with EITHER:
  1. A single fenced python code block to execute next, e.g.:
     ```python
     <code>
     ```
  2. Or, once you are done, a line starting with "FINAL:" summarizing what
     you did. Do not include a code block in a FINAL response.

You will see the stdout/stderr of each code block you run as
"Observation: ...". Inspect the sheet before making changes, and save your
answer to OUTPUT_PATH before finishing.
"""

SINGLE_ROUND_SYSTEM_PROMPT = """You are an agent that manipulates spreadsheets by
writing Python code (openpyxl or pandas).

WORKBOOK_PATH and OUTPUT_PATH are already defined as plain Python string
variables at the top of your code -- they are NOT environment variables
and there is nothing to search for on disk. Just reference them directly
by name, for example:
    import openpyxl
    wb = openpyxl.load_workbook(WORKBOOK_PATH)
    ...
    wb.save(OUTPUT_PATH)
Do not use os.environ, glob, or any file-discovery logic to find the
workbook.

You get exactly one turn: respond with a single fenced ```python code block
that reads WORKBOOK_PATH, does the task, and saves the result to
OUTPUT_PATH.
"""

_CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


@dataclass
class TrajectoryStep:
    turn: int
    response_text: str
    code: Optional[str]
    stdout: str
    stderr: str
    is_final: bool


@dataclass
class Trajectory:
    task_id: str
    tone_level: str
    trial: int
    steps: list[TrajectoryStep] = field(default_factory=list)
    final_output_path: Optional[Path] = None
    final_code: Optional[str] = None  # the code snippet that produced final_output_path
    refused: bool = False
    hit_turn_limit: bool = False  # ran out of max_turns without a FINAL response -- see failure_taxonomy.py
    result_rows: list[ResultRow] = field(default_factory=list)

    @property
    def code_snippets_in_order(self) -> list[str]:
        return [s.code for s in self.steps if s.code]


def _extract_code(text: str) -> Optional[str]:
    m = _CODE_BLOCK_RE.search(text)
    return m.group(1) if m else None


def _call_and_record(
    tracker: SpendTracker,
    model: ModelConfig,
    system: str,
    messages: list[dict],
    task_id: str,
    tone_level: str,
    trial: int,
    phase: str,
    turn: int,
):
    provider = get_provider(model.provider)
    tracker.check_before_call(estimated_cost_usd=0.02)
    _t0 = time.perf_counter()
    response = provider.complete(model, system, messages)
    if not response.latency_s:
        # Provider._timed() exists but OpenAICompatibleProvider.complete()
        # never calls it, so every row logged latency_s=0.0 and per-call timing
        # had to be inferred from timestamp gaps. Timed here instead of inside
        # one provider so it holds for all of them. Note this is wall time for
        # the whole call INCLUDING retry backoff, which is the number worth
        # having: it is what made Qwen 3x slower than the rest of the roster.
        response.latency_s = round(time.perf_counter() - _t0, 3)
    cost = compute_cost_usd(model, response)
    row = ResultRow(
        row_id=str(uuid.uuid4()),
        study="study2",
        phase=phase,
        item_id=task_id,
        tone_level=tone_level,
        trial=trial,
        model_key=model.key,
        model_id=model.model_id,
        provider=model.provider,
        temperature=model.temperature,
        seed=model.seed,
        reasoning_effort=model.reasoning_effort,
        thinking_budget_tokens=model.thinking_budget_tokens,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        reasoning_tokens=response.reasoning_tokens,
        cost_usd=cost,
        latency_s=response.latency_s,
        refused=response.refused,
        error=response.error,
        response_text=response.text,
        extracted_answer=None,
        is_correct=None,
        timestamp=time.time(),
        cached_tokens=response.cached_tokens,
        served_provider=response.served_provider,
        thinking_enabled=model.thinking_enabled,
        canonical_slug=model.canonical_slug,
        raw_response=response.raw,
        extra={"turn": turn},
    )
    tracker.record(row)
    return response, row


def run_single_round(
    tracker: SpendTracker,
    model: ModelConfig,
    task_id: str,
    instruction: str,
    workbook_path: Path,
    workdir: Path,
    tone_level: str,
    trial: int,
) -> Trajectory:
    traj = Trajectory(task_id=task_id, tone_level=tone_level, trial=trial)
    messages = [{"role": "user", "content": instruction}]
    response, row = _call_and_record(
        tracker, model, SINGLE_ROUND_SYSTEM_PROMPT, messages, task_id, tone_level, trial, "single_round", turn=0,
    )
    traj.result_rows.append(row)
    if response.refused:
        traj.refused = True
        traj.steps.append(TrajectoryStep(0, response.text, None, "", "", is_final=True))
        return traj

    code = _extract_code(response.text)
    stdout = stderr = ""
    output_path = None
    if code:
        exec_result = execute_python_on_workbook(code, workbook_path, workdir)
        stdout, stderr = exec_result.stdout, exec_result.stderr
        output_path = exec_result.output_workbook_path
    traj.steps.append(TrajectoryStep(0, response.text, code, stdout, stderr, is_final=True))
    traj.final_output_path = output_path
    traj.final_code = code if output_path else None
    return traj


def run_react_multi_round(
    tracker: SpendTracker,
    model: ModelConfig,
    task_id: str,
    instruction: str,
    workbook_path: Path,
    workdir: Path,
    tone_level: str,
    trial: int,
    max_turns: int = 10,  # was 6. Raised while chasing a 0/5 gate that turned out to be sandbox.py's
    # path bug, not a turn shortage (see _agent_system_prompt's CORRECTED note). Kept at 10 on the
    # post-fix evidence rather than reverted: with execution actually working, 4 of 5 gate tasks
    # converge in 3-4 turns, but the 5th still used all 10 -- so 10 is real headroom for the harder
    # tail, and costs nothing on the tasks that finish early since the loop breaks on FINAL.
) -> Trajectory:
    traj = Trajectory(task_id=task_id, tone_level=tone_level, trial=trial)
    messages = [{"role": "user", "content": instruction}]

    system_prompt = _agent_system_prompt(max_turns)
    for turn in range(max_turns):
        response, row = _call_and_record(
            tracker, model, system_prompt, messages, task_id, tone_level, trial, "multi_round_react", turn,
        )
        traj.result_rows.append(row)

        if response.refused:
            traj.refused = True
            traj.steps.append(TrajectoryStep(turn, response.text, None, "", "", is_final=True))
            break

        messages.append({"role": "assistant", "content": response.text})

        if response.text.strip().upper().startswith("FINAL:"):
            traj.steps.append(TrajectoryStep(turn, response.text, None, "", "", is_final=True))
            break

        turn_marker = f" [Turn {turn + 2} of {max_turns} next]" if turn + 2 <= max_turns else " [This was your last turn]"

        code = _extract_code(response.text)
        if not code:
            # Model didn't follow the protocol; feed that back as an observation
            # rather than silently ending the trajectory, then keep going.
            messages.append(
                {"role": "user", "content": "Observation: no code block or FINAL: line found. Please respond with one or the other." + turn_marker}
            )
            traj.steps.append(TrajectoryStep(turn, response.text, None, "", "", is_final=False))
            continue

        exec_result = execute_python_on_workbook(code, workbook_path, workdir / f"turn_{turn}")
        observation = (
            f"Observation: stdout={exec_result.stdout!r} stderr={exec_result.stderr!r} "
            f"timed_out={exec_result.timed_out}{turn_marker}"
        )
        messages.append({"role": "user", "content": observation})
        traj.steps.append(TrajectoryStep(turn, response.text, code, exec_result.stdout, exec_result.stderr, is_final=False))
        if exec_result.output_workbook_path:
            traj.final_output_path = exec_result.output_workbook_path
            traj.final_code = code
    else:
        traj.steps.append(TrajectoryStep(max_turns, "", None, "", "[max_turns reached without FINAL]", is_final=True))
        traj.hit_turn_limit = True

    return traj
