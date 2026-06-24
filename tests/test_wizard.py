from pathlib import Path
import json

from agent_loop.wizard import detect_checks


def test_detects_python_checks(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    commands = [check.command for check in detect_checks(tmp_path)]
    assert any("pytest" in command for command in commands)
    assert any("compileall" in command for command in commands)


def test_detects_node_scripts(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"scripts": {"test": "vitest", "build": "vite build"}}),
        encoding="utf-8",
    )

    commands = [check.command for check in detect_checks(tmp_path)]
    assert "npm run test" in commands
    assert "npm run build" in commands


def test_guided_setup_creates_config_only_after_explicit_choices(tmp_path: Path, monkeypatch) -> None:
    from types import SimpleNamespace
    from agent_loop.wizard import run_wizard

    project = tmp_path / "demo-project"
    project.mkdir()
    (project / ".git").mkdir()
    (project / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    (project / "tests").mkdir()

    answers = iter(
        [
            "1",  # Claude Code
            "",  # approve version check
            str(project),
            "Add a validation message",
            "Invalid input shows a message and tests pass",
            "4",
            "CREATE",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    monkeypatch.setattr("agent_loop.wizard.shutil.which", lambda name: f"/fake/{name}")
    monkeypatch.setattr(
        "agent_loop.wizard.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="2.1.185 (Claude Code)\n", stderr=""),
    )

    config_path = run_wizard()

    assert config_path == project / ".agent-loop" / "quick-start.toml"
    content = config_path.read_text(encoding="utf-8")
    assert 'project_dir = ' in content
    assert "Add a validation message" in content
    assert "agent_loop.agents claude" in content
    assert "pytest" in content
