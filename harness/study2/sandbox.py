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
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    output_path = workdir / "output.xlsx"

    script = _RUNNER_TEMPLATE.format(
        cpu=CPU_TIME_LIMIT_S,
        mem=MEM_LIMIT_BYTES,
        workdir=str(workdir),
        workbook_path=str(workbook_path),
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
