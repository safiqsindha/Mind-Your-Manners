"""Executes model-generated Python code against a spreadsheet workbook.

SECURITY NOTE: this runs arbitrary model-generated code. Isolation has two
layers, and only the first is verified:

  1. Network isolation via a Linux user+network namespace (`unshare --net
     --user --map-root-user --pid --mount-proc`), when the `unshare` binary
     is available. This is genuinely tested -- see tests/test_sandbox.py --
     not aspirational: a subprocess run this way cannot reach the network at
     all (confirmed: `socket.create_connection` raises "Network is
     unreachable" inside the namespace). If `unshare` is unavailable, this
     falls back to no network isolation and logs a one-time warning; check
     `sandbox_isolation_mode()` before trusting a live run's isolation.
  2. Resource limits (CPU/memory/wall-clock) and a stripped environment, as
     before.

What this does NOT do: restrict filesystem access. The namespaced process
still runs as the same (mapped-root) user with the same view of the
filesystem as the harness itself -- it just can't reach the network. Model-
generated code can still read/write anything the harness process can. For a
live run that spends real money, still prefer a proper container (Docker
with network disabled + a throwaway filesystem + a non-root user, or
gVisor) if available in your environment; this module's namespace-based
isolation is what's actually available and tested in a typical Claude Code
remote session, where a Docker daemon is usually not running (confirmed:
`docker info` fails here with "daemon is running?" -- there's a client
binary but no server to talk to).
"""
from __future__ import annotations

import functools
import resource
import shutil
import subprocess
import sys
import textwrap
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

CPU_TIME_LIMIT_S = 30
MEM_LIMIT_BYTES = 1_500_000_000
WALL_CLOCK_TIMEOUT_S = 60

_UNSHARE_NET_ARGS = ["--net", "--user", "--map-root-user", "--pid", "--mount-proc", "--fork", "--"]


@functools.lru_cache(maxsize=1)
def sandbox_isolation_mode() -> str:
    """Returns "namespace" if network isolation via `unshare` is both
    present AND actually usable on this host, else "none". The `unshare`
    binary being on PATH is not sufficient -- user-namespace creation can
    be permission-denied even for root, and this varies by host: it
    succeeds in this project's own dev/build environment but fails on a
    default GitHub Actions ubuntu-latest runner with "write failed
    /proc/self/uid_map: Operation not permitted" (confirmed via a real CI
    run -- see git history). So this actually attempts a trivial
    `unshare --net --user --map-root-user ... true` and checks it
    succeeds, rather than assuming binary-presence implies it works.
    Callers/tests should check this rather than assuming network isolation
    is active -- see module docstring."""
    if shutil.which("unshare") is None:
        warnings.warn(
            "`unshare` binary not found -- Study 2's code sandbox has NO network "
            "isolation on this host. Do not run a live, spend-worthy Study 2 batch "
            "without fixing this (install util-linux, or run inside a container).",
            stacklevel=2,
        )
        return "none"

    probe = subprocess.run(
        ["unshare", *_UNSHARE_NET_ARGS, "true"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if probe.returncode != 0:
        warnings.warn(
            "`unshare` is present but namespace creation failed on this host "
            f"({probe.stderr.strip()!r}) -- Study 2's code sandbox has NO network "
            "isolation here. Do not run a live, spend-worthy Study 2 batch without "
            "fixing this (run as a user allowed to create user namespaces, or use a "
            "container instead).",
            stacklevel=2,
        )
        return "none"
    return "namespace"


_RUNNER_TEMPLATE = """
import resource, sys
resource.setrlimit(resource.RLIMIT_CPU, ({cpu}, {cpu}))
resource.setrlimit(resource.RLIMIT_AS, ({mem}, {mem}))
sys.path.insert(0, {workdir!r})

WORKBOOK_PATH = {workbook_path!r}
OUTPUT_PATH = {output_path!r}

{code}
"""


@dataclass(frozen=True)
class ExecutionResult:
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool
    output_workbook_path: Path | None
    network_isolated: bool  # True iff this call actually ran inside the unshare net namespace


def execute_python_on_workbook(code: str, workbook_path: Path, workdir: Path) -> ExecutionResult:
    """Runs `code` in a subprocess with WORKBOOK_PATH and OUTPUT_PATH
    pre-bound as variables. Convention: the agent's code should read
    WORKBOOK_PATH (openpyxl/pandas) and write its result to OUTPUT_PATH."""
    # Both paths MUST be absolute before anything below uses them. The
    # subprocess is launched with cwd=workdir, so any relative path handed to
    # it is re-resolved against that new cwd rather than the harness's own.
    # That silently doubled the script path (".../59196_t0/results/scratch/
    # .../59196_t0/_agent_code.py") and made every single execution fail with
    # "can't open file" before running one line of model code -- in every
    # real run, since the CLI's out_dir is relative, while every test passed
    # an absolute tmp_path and so never reproduced it. WORKBOOK_PATH is
    # resolved for the same reason: it's injected into the child as a literal
    # and read after the cwd change. See tests/test_sandbox.py's
    # relative-path regression tests.
    workdir = Path(workdir).resolve()
    workbook_path = Path(workbook_path).resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    output_path = workdir / "output.xlsx"
    # Success is reported below as output_path.exists(), which is only a claim
    # about THIS execution if nothing was there beforehand. Left in place, a
    # stale file from an earlier run means code that crashes without writing
    # anything is still reported as having produced output -- and the grader
    # then scores the previous run's answer. That is not hypothetical: it
    # silently inflated a roster-wide gate baseline, where every model shared
    # one scratch directory and later models inherited earlier ones' passing
    # outputs (all four scored an identical 3/5; with the reuse removed, two
    # of them scored 2/5). Deleting it first makes existence afterwards mean
    # what the rest of this function assumes it means.
    output_path.unlink(missing_ok=True)

    # ANSWER-KEY ISOLATION. SpreadsheetBench stores each task's ground truth
    # beside its input -- spreadsheet/59196/1_59196_input.xlsx sits next to
    # 1_59196_answer.xlsx. Pointing WORKBOOK_PATH straight at the dataset made
    # the answer one os.listdir(os.path.dirname(WORKBOOK_PATH)) away, and this
    # sandbox deliberately does not restrict filesystem access (see module
    # docstring), so the only thing standing between a model and the answer key
    # was a system-prompt line asking it not to look.
    #
    # No model exploited it across the four validation runs (checked: zero
    # turns referencing an answer path, listdir, glob or os.walk). That is not
    # a guarantee for 4,200 core-run trajectories, and it is a particularly bad
    # risk for THIS study: the manipulation is tone, so if corner-cutting rises
    # under, say, threatening prompts, the leak would show up as a tone effect
    # on accuracy while looking exactly like a legitimate pass.
    #
    # Copying the input into the workdir closes it at the mechanism instead of
    # by instruction: dirname(WORKBOOK_PATH) is now a directory containing only
    # this turn's own files. The basename is preserved so extension checks
    # (a real one: .xlsm macro handling) still behave. Inputs are ~10KB median,
    # 929KB max, so the per-turn copy is free.
    sandbox_workbook = workdir / workbook_path.name
    shutil.copy(workbook_path, sandbox_workbook)

    script = _RUNNER_TEMPLATE.format(
        cpu=CPU_TIME_LIMIT_S,
        mem=MEM_LIMIT_BYTES,
        workdir=str(workdir),
        workbook_path=str(sandbox_workbook),
        output_path=str(output_path),
        code=textwrap.indent(code, ""),
    )
    script_path = workdir / "_agent_code.py"
    script_path.write_text(script)

    env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"}
    base_cmd = [sys.executable, str(script_path)]
    network_isolated = sandbox_isolation_mode() == "namespace"
    cmd = ["unshare", *_UNSHARE_NET_ARGS, *base_cmd] if network_isolated else base_cmd

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workdir),
            env=env,
            capture_output=True,
            text=True,
            timeout=WALL_CLOCK_TIMEOUT_S,
        )
        timed_out = False
        returncode = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        returncode = -1
        stdout, stderr = (e.stdout or ""), (e.stderr or "") + "\n[execution timed out]"

    return ExecutionResult(
        stdout=stdout,
        stderr=stderr,
        returncode=returncode,
        timed_out=timed_out,
        output_workbook_path=output_path if output_path.exists() else None,
        network_isolated=network_isolated,
    )
