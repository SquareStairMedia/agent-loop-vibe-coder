from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import ConfigError, load_config
from .runner import run_loop
from .wizard import run_wizard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-loop",
        description="Run a bounded coding-agent loop and verify its work with deterministic commands.",
    )
    subparsers = parser.add_subparsers(dest="command")

    start = subparsers.add_parser(
        "start",
        help="First-time-user guided setup",
        description="Create and optionally run an agent loop by answering plain-English questions.",
    )
    start.add_argument(
        "--setup-only",
        action="store_true",
        help="Create the configuration without running the coding agent",
    )
    start.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional directory for prompts, logs, verification results, and outcomes",
    )

    run = subparsers.add_parser(
        "run",
        help="Run an existing TOML configuration",
        description="Run an existing advanced TOML loop configuration.",
    )
    run.add_argument("config", type=Path, help="Path to a TOML loop configuration")
    run.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional directory for prompts, logs, verification results, and outcomes",
    )
    run.add_argument(
        "--allow-agent",
        action="store_true",
        help="Required acknowledgement that the configured agent command may edit files and execute tools",
    )
    return parser


def _run_config(config_path: Path, output_dir: Path | None, allow_agent: bool) -> int:
    if not allow_agent:
        print("Refusing to invoke the agent without --allow-agent.", file=sys.stderr)
        return 2
    try:
        config = load_config(config_path.resolve())
    except (OSError, ConfigError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    resolved_output_dir = output_dir or (config.project_dir / ".agent-loop" / "runs")
    outcome = run_loop(config, resolved_output_dir)
    print("\nRun finished")
    print(f"Passed: {outcome.passed}")
    print(f"Why it stopped: {outcome.stop_reason}")
    print(f"Attempts used: {outcome.iterations}")
    print(f"Detailed record: {outcome.run_dir}")
    return 0 if outcome.passed else 1


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if raw_args and raw_args[0] not in {"start", "run", "-h", "--help"}:
        raw_args.insert(0, "run")
    args = build_parser().parse_args(raw_args)

    if args.command == "start":
        config_path = run_wizard()
        if config_path is None:
            return 2
        if args.setup_only:
            return 0

        print("\nThe setup is complete. Nothing has run yet.")
        print("Starting will allow the selected AI coding agent to edit the chosen project and run tools there.")
        answer = input("Type RUN to start the loop now, or press Enter to stop: ").strip()
        if answer != "RUN":
            print(f"Not started. Run it later with: agent-loop run \"{config_path}\" --allow-agent")
            return 0
        return _run_config(config_path, args.output_dir, allow_agent=True)

    if args.command == "run":
        return _run_config(args.config, args.output_dir, args.allow_agent)

    build_parser().print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
