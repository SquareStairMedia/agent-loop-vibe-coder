from pathlib import Path

import pytest

from agent_loop.config import ConfigError, load_config


def test_loads_valid_config(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config = tmp_path / "loop.toml"
    config.write_text(
        f'''[loop]\nname = "demo"\nproject_dir = "{project.as_posix()}"\ntask = "Fix it"\nacceptance_criteria = ["Tests pass"]\nagent_command = "agent --file {{prompt_file}}"\n\n[[verify]]\nname = "tests"\ncommand = "python -m pytest"\n''',
        encoding="utf-8",
    )

    loaded = load_config(config)
    assert loaded.name == "demo"
    assert loaded.verify[0].name == "tests"


def test_rejects_config_without_verifier(tmp_path: Path) -> None:
    config = tmp_path / "loop.toml"
    config.write_text(
        '[loop]\nname="demo"\nproject_dir="."\ntask="Fix"\nacceptance_criteria=["Pass"]\nagent_command="agent"\n',
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="verify"):
        load_config(config)
