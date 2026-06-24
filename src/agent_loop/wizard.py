from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import shutil
import subprocess
import sys


@dataclass(frozen=True)
class SuggestedCheck:
    name: str
    command: str
    reason: str


@dataclass(frozen=True)
class AgentChoice:
    key: str
    label: str
    version_command: tuple[str, ...]


AGENTS = (
    AgentChoice("claude", "Claude Code", ("claude", "--version")),
    AgentChoice("codex", "Codex CLI", ("codex", "--version")),
)


def detect_checks(project_dir: Path) -> list[SuggestedCheck]:
    checks: list[SuggestedCheck] = []

    package_json = project_dir / "package.json"
    if package_json.is_file():
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
            scripts = package.get("scripts", {}) if isinstance(package, dict) else {}
        except (OSError, json.JSONDecodeError):
            scripts = {}
        if isinstance(scripts, dict):
            for script, reason in (
                ("test", "runs the project's automated tests"),
                ("build", "confirms the project still builds"),
                ("lint", "checks common code-quality errors"),
                ("typecheck", "checks type errors"),
                ("type-check", "checks type errors"),
            ):
                if script in scripts:
                    checks.append(SuggestedCheck(script, f"npm run {script}", reason))

    python_project = any((project_dir / name).is_file() for name in ("pyproject.toml", "setup.py", "requirements.txt"))
    if python_project:
        if (project_dir / "tests").is_dir():
            checks.append(SuggestedCheck("tests", f'"{sys.executable}" -m pytest -q', "runs the project's automated tests"))
        checks.append(SuggestedCheck("syntax", f'"{sys.executable}" -m compileall -q .', "checks that Python files compile"))

    if shutil.which("git") and (project_dir / ".git").exists():
        checks.append(SuggestedCheck("git-diff", "git diff --check", "detects malformed conflict markers and whitespace errors"))

    unique: list[SuggestedCheck] = []
    seen: set[str] = set()
    for check in checks:
        if check.command not in seen:
            unique.append(check)
            seen.add(check.command)
    return unique


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        print("Please enter a value.")


def _yes_no(prompt: str, default: bool = True) -> bool:
    label = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{label}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes"}


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _choose_agent() -> AgentChoice | None:
    print("Step 1 of 5: Choose the AI coding agent you already use")
    print("This loop does not include an AI model. It supervises an installed coding agent.\n")
    for index, agent in enumerate(AGENTS, start=1):
        print(f"  {index}. {agent.label}")
    print("  3. I do not have either one installed yet")

    while True:
        choice = _ask("Choose 1, 2, or 3")
        if choice == "3":
            print("\nInstall and sign in to Claude Code or Codex first, then run 'agent-loop start' again.")
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(AGENTS):
            return AGENTS[int(choice) - 1]
        print("Enter 1, 2, or 3.")


def _confirm_agent(agent: AgentChoice) -> bool:
    command_text = " ".join(agent.version_command)
    print(f"\nTo confirm {agent.label} is available, this tool will run only:")
    print(f"  {command_text}")
    print("It will not search your files or inspect unrelated folders.")
    if not _yes_no("Run this check now?", True):
        print(f"Run '{command_text}' yourself, then start again when it succeeds.")
        return False

    executable = shutil.which(agent.version_command[0])
    if executable is None:
        print(f"\n{agent.label} was not found in your terminal PATH.", file=sys.stderr)
        print(f"Run '{command_text}' manually. If it fails, install or repair {agent.label} first.", file=sys.stderr)
        return False

    try:
        completed = subprocess.run(
            [executable, *agent.version_command[1:]],
            text=True,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"Could not run the version check: {exc}", file=sys.stderr)
        return False

    output = (completed.stdout or completed.stderr).strip()
    if completed.returncode != 0:
        print(f"The check failed: {output or 'no error details were returned'}", file=sys.stderr)
        return False

    print(f"Confirmed: {output or agent.label}")
    return True


def _choose_project_dir() -> Path | None:
    print("\nStep 2 of 5: Choose the coding project the loop may change")
    print("Enter the full path to a separate project folder.")
    print("Do not enter the folder that contains this agent-loop tool.")
    print(r"Example: D:\SquareStairMedia\dev\my-test-project")

    project_dir = Path(_ask("Project folder path")).expanduser().resolve()
    if not project_dir.is_dir():
        print(f"That folder does not exist: {project_dir}", file=sys.stderr)
        return None

    if not (project_dir / ".git").is_dir():
        print("\nThis folder is not a Git repository.", file=sys.stderr)
        print("For safety, initialize Git or choose a project that already uses Git before running an AI agent.", file=sys.stderr)
        print(f'Open PowerShell in that project and run: git init', file=sys.stderr)
        return None

    print(f"Selected project: {project_dir}")
    return project_dir


def _write_config(
    path: Path,
    project_dir: Path,
    task: str,
    criterion: str,
    provider: str,
    checks: list[SuggestedCheck],
    max_iterations: int,
) -> None:
    python = str(Path(sys.executable).resolve())
    agent_command = f'"{python}" -m agent_loop.agents {provider} "{{prompt_file}}"'

    lines = [
        "[loop]",
        f'name = {_toml_string("vibe-loop")}',
        f'project_dir = {_toml_string(str(project_dir.resolve()))}',
        f'task = {_toml_string(task)}',
        "acceptance_criteria = [",
        f"  {_toml_string(criterion)},",
        '  "All selected verification checks pass.",',
        "]",
        f"max_iterations = {max_iterations}",
        "max_elapsed_seconds = 1800",
        "agent_timeout_seconds = 900",
        f'agent_command = {_toml_string(agent_command)}',
        "",
    ]
    for check in checks:
        lines.extend(
            [
                "[[verify]]",
                f'name = {_toml_string(check.name)}',
                f'command = {_toml_string(check.command)}',
                "timeout_seconds = 300",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_wizard() -> Path | None:
    print("\nAgent Loop guided setup")
    print("This tool supervises Claude Code or Codex while it works on one coding project.")
    print("The AI agent edits the project. This tool runs checks and decides whether another attempt is needed.")
    print("Nothing will edit files until you review a final summary and explicitly approve the run.\n")

    agent = _choose_agent()
    if agent is None or not _confirm_agent(agent):
        return None

    project_dir = _choose_project_dir()
    if project_dir is None:
        return None

    print("\nStep 3 of 5: Describe one specific coding task")
    print("Example: Add a contact form validation message when the email address is invalid.")
    task = _ask("What should the AI coding agent change?")

    print("\nStep 4 of 5: Describe what success looks like")
    print("Use something a person could observe or a test could prove.")
    print("Example: Invalid email addresses show a clear message and the existing tests still pass.")
    criterion = _ask("What must be true when the task is finished?")

    checks = detect_checks(project_dir)
    if not checks:
        print("\nNo trustworthy automatic verification was found in this project.", file=sys.stderr)
        print("The loop will not run because it would have no reliable way to know the work is complete.", file=sys.stderr)
        print("Choose a project with tests, a build command, linting, type checks, or a Python compile check.", file=sys.stderr)
        return None

    print("\nVerification checks found in your project:")
    for check in checks:
        print(f"  - {check.command}")
        print(f"    Why: {check.reason}")

    print("\nStep 5 of 5: Set the retry limit")
    print("Four attempts is a sensible beginner default. The loop stops earlier if all checks pass.")
    max_iterations_text = _ask("Maximum attempts", "4")
    try:
        max_iterations = max(1, int(max_iterations_text))
    except ValueError:
        print("Maximum attempts must be a whole number.", file=sys.stderr)
        return None

    print("\nFinal review")
    print("The loop is prepared to:")
    print(f"  AI agent: {agent.label}")
    print(f"  Project it may modify: {project_dir}")
    print(f"  Task: {task}")
    print(f"  Success condition: {criterion}")
    print(f"  Maximum attempts: {max_iterations}")
    print("  Verification:")
    for check in checks:
        print(f"    - {check.command}")
    print("\nThe AI agent may edit files and run coding tools inside the selected project folder.")

    if input("Type CREATE to save this loop, or press Enter to cancel: ").strip() != "CREATE":
        print("Cancelled. No configuration was created.")
        return None

    config_path = project_dir / ".agent-loop" / "quick-start.toml"
    _write_config(config_path, project_dir, task, criterion, agent.key, checks, max_iterations)
    print(f"\nLoop configuration created: {config_path}")
    return config_path
