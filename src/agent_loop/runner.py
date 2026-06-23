from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import time

from .config import LoopConfig
from .process import ProcessResult, run_process


@dataclass(frozen=True)
class VerificationResult:
    name: str
    passed: bool
    process: ProcessResult

    def to_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "process": self.process.to_dict()}


@dataclass(frozen=True)
class LoopOutcome:
    passed: bool
    stop_reason: str
    iterations: int
    run_dir: Path


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _format_failures(results: list[VerificationResult]) -> str:
    failures = [result for result in results if not result.passed]
    if not failures:
        return "No previous verification failures."

    sections: list[str] = []
    for failure in failures:
        process = failure.process
        sections.append(
            f"### {failure.name}\n"
            f"Command: `{process.command}`\n"
            f"Exit code: {process.exit_code}\n"
            f"Timed out: {process.timed_out}\n\n"
            f"STDOUT:\n```\n{process.stdout[-6000:]}\n```\n\n"
            f"STDERR:\n```\n{process.stderr[-6000:]}\n```"
        )
    return "\n\n".join(sections)


def _build_prompt(config: LoopConfig, iteration: int, previous: list[VerificationResult]) -> str:
    criteria = "\n".join(f"- {item}" for item in config.acceptance_criteria)
    return f"""# Coding task

{config.task}

# Acceptance criteria

{criteria}

# Current iteration

{iteration} of {config.max_iterations}

# Verification feedback from the previous iteration

{_format_failures(previous)}

# Operating instructions

Work only inside the current project directory. Inspect the existing code before editing. Make the smallest coherent change that satisfies the task. Do not weaken, remove, skip, or rewrite verification merely to make it pass. Do not claim success; the harness will determine success from command results. When finished, leave the working tree containing your best implementation and exit.
"""


def _render_agent_command(template: str, prompt_file: Path, run_dir: Path, iteration: int) -> str:
    return template.format(
        prompt_file=str(prompt_file),
        run_dir=str(run_dir),
        iteration=iteration,
    )


def run_loop(config: LoopConfig, output_root: Path) -> LoopOutcome:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = (output_root / f"{timestamp}-{config.name}").resolve()
    run_dir.mkdir(parents=True, exist_ok=False)

    _write_json(run_dir / "config.snapshot.json", {
        **asdict(config),
        "project_dir": str(config.project_dir),
        "verify": [asdict(v) for v in config.verify],
    })

    started = time.monotonic()
    previous: list[VerificationResult] = []

    for iteration in range(1, config.max_iterations + 1):
        if time.monotonic() - started >= config.max_elapsed_seconds:
            return _finish(run_dir, False, "elapsed-time-limit", iteration - 1)

        iteration_dir = run_dir / f"iteration-{iteration:02d}"
        iteration_dir.mkdir()
        prompt_file = iteration_dir / "prompt.md"
        prompt_file.write_text(_build_prompt(config, iteration, previous), encoding="utf-8")

        agent_command = _render_agent_command(config.agent_command, prompt_file, run_dir, iteration)
        agent_result = run_process(
            agent_command,
            cwd=config.project_dir,
            timeout_seconds=config.agent_timeout_seconds,
            env={
                "AGENT_LOOP_PROMPT_FILE": str(prompt_file),
                "AGENT_LOOP_RUN_DIR": str(run_dir),
                "AGENT_LOOP_ITERATION": str(iteration),
            },
        )
        _write_json(iteration_dir / "agent.json", agent_result.to_dict())

        verification: list[VerificationResult] = []
        for check in config.verify:
            process = run_process(check.command, config.project_dir, check.timeout_seconds)
            verification.append(
                VerificationResult(
                    name=check.name,
                    passed=(not process.timed_out and process.exit_code == 0),
                    process=process,
                )
            )

        _write_json(iteration_dir / "verification.json", [item.to_dict() for item in verification])

        if all(item.passed for item in verification):
            return _finish(run_dir, True, "verification-passed", iteration)

        previous = verification

    return _finish(run_dir, False, "iteration-limit", config.max_iterations)


def _finish(run_dir: Path, passed: bool, stop_reason: str, iterations: int) -> LoopOutcome:
    outcome = LoopOutcome(passed=passed, stop_reason=stop_reason, iterations=iterations, run_dir=run_dir)
    _write_json(run_dir / "outcome.json", {
        "passed": passed,
        "stop_reason": stop_reason,
        "iterations": iterations,
        "run_dir": str(run_dir),
    })
    return outcome
