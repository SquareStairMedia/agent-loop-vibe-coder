from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import tomllib


class ConfigError(ValueError):
    """Raised when a loop configuration is invalid."""


@dataclass(frozen=True)
class VerifyCommand:
    name: str
    command: str
    timeout_seconds: int = 300


@dataclass(frozen=True)
class LoopConfig:
    name: str
    task: str
    acceptance_criteria: tuple[str, ...]
    agent_command: str
    project_dir: Path
    max_iterations: int = 5
    max_elapsed_seconds: int = 1800
    agent_timeout_seconds: int = 900
    verify: tuple[VerifyCommand, ...] = field(default_factory=tuple)


def _required_str(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"'{key}' must be a non-empty string")
    return value.strip()


def load_config(path: Path) -> LoopConfig:
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    loop = raw.get("loop")
    if not isinstance(loop, dict):
        raise ConfigError("Missing [loop] section")

    criteria = loop.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria or not all(isinstance(x, str) and x.strip() for x in criteria):
        raise ConfigError("'acceptance_criteria' must be a non-empty list of strings")

    verify_raw = raw.get("verify", [])
    if not isinstance(verify_raw, list) or not verify_raw:
        raise ConfigError("At least one [[verify]] command is required")

    verify: list[VerifyCommand] = []
    for item in verify_raw:
        if not isinstance(item, dict):
            raise ConfigError("Each [[verify]] entry must be a table")
        verify.append(
            VerifyCommand(
                name=_required_str(item, "name"),
                command=_required_str(item, "command"),
                timeout_seconds=int(item.get("timeout_seconds", 300)),
            )
        )

    project_dir = Path(loop.get("project_dir", ".")).expanduser()
    if not project_dir.is_absolute():
        project_dir = (path.parent / project_dir).resolve()

    config = LoopConfig(
        name=_required_str(loop, "name"),
        task=_required_str(loop, "task"),
        acceptance_criteria=tuple(x.strip() for x in criteria),
        agent_command=_required_str(loop, "agent_command"),
        project_dir=project_dir,
        max_iterations=int(loop.get("max_iterations", 5)),
        max_elapsed_seconds=int(loop.get("max_elapsed_seconds", 1800)),
        agent_timeout_seconds=int(loop.get("agent_timeout_seconds", 900)),
        verify=tuple(verify),
    )

    if config.max_iterations < 1:
        raise ConfigError("'max_iterations' must be at least 1")
    if config.max_elapsed_seconds < 1 or config.agent_timeout_seconds < 1:
        raise ConfigError("Timeout values must be positive")
    if not config.project_dir.is_dir():
        raise ConfigError(f"Project directory does not exist: {config.project_dir}")

    return config
