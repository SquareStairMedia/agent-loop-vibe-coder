from pathlib import Path

from agent_loop.config import LoopConfig, VerifyCommand
from agent_loop.runner import run_loop


def test_loop_passes_after_agent_creates_expected_file(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    output = tmp_path / "runs"
    config = LoopConfig(
        name="create-marker",
        task="Create marker.txt",
        acceptance_criteria=("marker.txt exists",),
        agent_command='python -c "from pathlib import Path; Path(\'marker.txt\').write_text(\'ok\')"',
        project_dir=project,
        max_iterations=2,
        verify=(VerifyCommand(name="marker", command='python -c "from pathlib import Path; assert Path(\'marker.txt\').read_text() == \'ok\'"'),),
    )

    outcome = run_loop(config, output)
    assert outcome.passed is True
    assert outcome.iterations == 1
    assert (outcome.run_dir / "outcome.json").exists()


def test_loop_stops_at_iteration_limit(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config = LoopConfig(
        name="never-passes",
        task="Impossible task",
        acceptance_criteria=("Verifier passes",),
        agent_command='python -c "print(\'attempted\')"',
        project_dir=project,
        max_iterations=2,
        verify=(VerifyCommand(name="fail", command='python -c "raise SystemExit(1)"'),),
    )

    outcome = run_loop(config, tmp_path / "runs")
    assert outcome.passed is False
    assert outcome.stop_reason == "iteration-limit"
    assert outcome.iterations == 2
