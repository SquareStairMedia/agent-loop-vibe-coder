from pathlib import Path
from types import SimpleNamespace

from agent_loop import agents


def test_claude_uses_scripted_file_edit_permissions(tmp_path: Path, monkeypatch) -> None:
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Fix it", encoding="utf-8")
    captured = {}

    monkeypatch.setattr(agents.shutil, "which", lambda name: f"/fake/{name}")

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["input"] = kwargs["input"]
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(agents.subprocess, "run", fake_run)
    assert agents.main(["claude", str(prompt)]) == 0
    assert "--permission-mode" in captured["command"]
    assert "acceptEdits" in captured["command"]
    assert "Read,Edit,Write,Glob,Grep" in captured["command"]
    assert captured["input"] == "Fix it"


def test_codex_uses_workspace_write_without_interactive_prompts(tmp_path: Path, monkeypatch) -> None:
    prompt = tmp_path / "prompt.md"
    prompt.write_text("Fix it", encoding="utf-8")
    captured = {}

    monkeypatch.setattr(agents.shutil, "which", lambda name: f"/fake/{name}")

    def fake_run(command, **kwargs):
        captured["command"] = command
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(agents.subprocess, "run", fake_run)
    assert agents.main(["codex", str(prompt)]) == 0
    assert captured["command"][-7:] == [
        "exec",
        "--sandbox",
        "workspace-write",
        "--ask-for-approval",
        "never",
        "--skip-git-repo-check",
        "-",
    ]
