from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import ConfigError, load_config
from .runner import run_loop


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-loop",
        description="Run a bounded coding-agent loop and verify its work with deterministic commands.",
    )
    parser.add_argument("config", type=Path, help="Path to a TOML loop configuration")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(".agent-loop/runs"),
        help="Directory for prompts, logs, verification results, and outcomes",
    )
    parser.add_argument(
        "--allow-agent",
        action="store_true",
        help="Required acknowledgement that the configured agent command may edit files and execute tools",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.allow_agent:
        print("Refusing to invoke the agent without --allow-agent.", file=sys.stderr)
        return 2

    try:
        config = load_config(args.config.resolve())
    except (OSError, ConfigError, ValueError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    outcome = run_loop(config, args.output_dir)
    print(f"Passed: {outcome.passed}")
    print(f"Stop reason: {outcome.stop_reason}")
    print(f"Iterations: {outcome.iterations}")
    print(f"Audit trail: {outcome.run_dir}")
    return 0 if outcome.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
