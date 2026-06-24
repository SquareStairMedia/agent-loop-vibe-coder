from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


def _run(command: list[str], prompt: str) -> int:
    executable = shutil.which(command[0])
    if executable is None:
        print(f"Could not find '{command[0]}' on PATH.", file=sys.stderr)
        return 127

    completed = subprocess.run(
        [executable, *command[1:]],
        input=prompt,
        text=True,
        check=False,
    )
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 2:
        print("Usage: python -m agent_loop.agents <claude|codex> <prompt-file>", file=sys.stderr)
        return 2

    provider, prompt_path = args
    prompt = Path(prompt_path).read_text(encoding="utf-8")

    if provider == "claude":
        # Claude Code print mode. The prompt is provided on stdin to avoid shell quoting issues.
        return _run(["claude", "-p"], prompt)
    if provider == "codex":
        # Codex exec reads the task from stdin when '-' is supplied.
        return _run(["codex", "exec", "-"], prompt)

    print(f"Unsupported agent provider: {provider}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
