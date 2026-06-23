from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import os
import subprocess
import time


@dataclass(frozen=True)
class ProcessResult:
    command: str
    exit_code: int | None
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool

    def to_dict(self) -> dict:
        return asdict(self)


def run_process(command: str, cwd: Path, timeout_seconds: int, env: dict[str, str] | None = None) -> ProcessResult:
    started = time.monotonic()
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=merged_env,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return ProcessResult(
            command=command,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            elapsed_seconds=round(time.monotonic() - started, 3),
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return ProcessResult(
            command=command,
            exit_code=None,
            stdout=stdout,
            stderr=stderr,
            elapsed_seconds=round(time.monotonic() - started, 3),
            timed_out=True,
        )
