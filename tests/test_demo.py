from pathlib import Path

from agent_loop.demo import create_demo_project, write_demo_config
from agent_loop.config import load_config


def test_demo_project_is_disposable_and_has_a_failing_example(tmp_path: Path) -> None:
    project = create_demo_project(tmp_path)
    assert project == tmp_path / "agent-loop-demo-project"
    assert (project / "app.py").is_file()
    assert (project / "tests" / "test_app.py").is_file()
    assert "return value.replace" in (project / "app.py").read_text(encoding="utf-8")


def test_demo_config_uses_bounded_verified_loop(tmp_path: Path) -> None:
    project = create_demo_project(tmp_path)
    config_path = write_demo_config(project, "claude")
    config = load_config(config_path)

    assert config.project_dir == project.resolve()
    assert config.max_iterations == 3
    assert len(config.verify) == 1
    assert "unittest discover" in config.verify[0].command
    assert "agent_loop.agents claude" in config.agent_command
