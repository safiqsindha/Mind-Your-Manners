"""Executes model-generated Python code against a spreadsheet workbook.

SECURITY NOTE: this runs arbitrary model-generated code. The subprocess
isolation here (separate process, CPU/memory/wall-clock limits, stripped
environment, no network env vars) is a floor, not a real sandbox boundary.
Before any live run that spends money, run this inside a proper container
(gVisor/Docker with network disabled, a fresh throwaway filesystem, and a
non-root user) -- do not rely on this module alone for isolation against a
model that has been told, across five conditions, to be adversarial in tone.
"""
from __future__ import annotations

import resource
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass
from pathlib import Path

CPU_TIME_LIMIT_S = 30
MEM_LIMIT_BYTES = 1_500_000_000
WALL_CLOCK_TIMEOUT_S = 60

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
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
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
    )
