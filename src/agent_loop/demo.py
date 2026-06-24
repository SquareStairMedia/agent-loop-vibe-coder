from __future__ import annotations

from pathlib import Path
import json
import shutil
import sys
import tempfile

from .config import load_config
from .runner import run_loop


DEMO_SOURCE = '''def slugify(value: str) -> str:
    """Return a simple URL slug."""
    return value.replace(" ", "-")
'''

DEMO_TEST = '''import unittest

from app import slugify


class SlugifyTests(unittest.TestCase):
    def test_slugify_lowercases_and_replaces_spaces(self) -> None:
        self.assertEqual(slugify("Hello World"), "hello-world")


if __name__ == "__main__":
    unittest.main()
'''


def create_demo_project(base_dir: Path | None = None) -> Path:
    if base_dir is None:
        project_dir = Path(tempfile.mkdtemp(prefix="agent-loop-demo-"))
    else:
        project_dir = (base_dir / "agent-loop-demo-project").resolve()
        if project_dir.exists():
            shutil.rmtree(project_dir)
        project_dir.mkdir(parents=True)

    (project_dir / "tests").mkdir(parents=True, exist_ok=True)
    (project_dir / "app.py").write_text(DEMO_SOURCE, encoding="utf-8")
    (project_dir / "tests" / "test_app.py").write_text(DEMO_TEST, encoding="utf-8")
    return project_dir


def write_demo_config(project_dir: Path, provider: str) -> Path:
    config_dir = project_dir / ".agent-loop"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "demo.toml"
    python = sys.executable
    agent_command = f'"{python}" -m agent_loop.agents {provider} "{{prompt_file}}"'
    verify_command = f'"{python}" -m unittest discover -s tests -v'

    config_path.write_text(
        "\n".join(
            [
                "[loop]",
                'name = "safe-demo"',
                f"project_dir = {json.dumps(str(project_dir))}",
                'task = "Fix slugify so it converts text to lowercase and replaces spaces with hyphens."',
                "acceptance_criteria = [",
                '  "slugify(\\\"Hello World\\\") returns \\\"hello-world\\\".",',
                '  "The included unit test passes.",',
                "]",
                "max_iterations = 3",
                "max_elapsed_seconds = 900",
                "agent_timeout_seconds = 300",
                f"agent_command = {json.dumps(agent_command)}",
                "",
                "[[verify]]",
                'name = "unit-tests"',
                f"command = {json.dumps(verify_command)}",
                "timeout_seconds = 120",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def run_demo(provider: str, base_dir: Path | None = None) -> int:
    project_dir = create_demo_project(base_dir)
    config_path = write_demo_config(project_dir, provider)

    print("\nSafe demo project created")
    print(f"Location: {project_dir}")
    print("This is a disposable project created only for the demo.")
    print("The AI agent will fix one small Python function, and a unit test will verify the result.")
    print("No existing project files will be touched.\n")

    answer = input("Type RUN DEMO to continue, or press Enter to cancel: ").strip()
    if answer != "RUN DEMO":
        print(f"Cancelled. The untouched demo project remains at: {project_dir}")
        return 0

    outcome = run_loop(load_config(config_path), project_dir / ".agent-loop" / "runs")
    print("\nDemo finished")
    print(f"Passed: {outcome.passed}")
    print(f"Why it stopped: {outcome.stop_reason}")
    print(f"Attempts used: {outcome.iterations}")
    print(f"Demo project: {project_dir}")
    print(f"Detailed record: {outcome.run_dir}")
    return 0 if outcome.passed else 1
