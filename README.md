# Verifiable Agent Loop

A practical coding-agent loop you can use immediately, with deterministic verification, bounded retries, complete audit trails, and guidance for designing effective loops of your own.

## The important clarification

A loop is not effective on its own. It becomes effective only when its goal, tools, evidence, acceptance criteria, limits, and human controls match the task.

This repository provides a strong coding-loop implementation because software work often has objective evidence: tests, builds, linters, type checks, and observable file changes. The loop structure is reusable. The verification strategy is not universal and must change with the use case.

## What it does

The harness:

1. reads a coding task and explicit acceptance criteria
2. gives the task and prior failures to a configured coding agent
3. lets the agent inspect and modify the target project
4. runs deterministic verification commands itself
5. repeats only when verification fails
6. stops when verification passes or a configured boundary is reached
7. stores every prompt, command result, failure, and outcome in an audit directory

The agent cannot mark its own work complete. Success is determined by evidence produced outside the model.

## Why this is different from a loop prompt

A prompt that says “review your work and keep improving it” is still asking the same model to judge itself. This project places the loop around the agent:

```text
objective -> agent action -> external evidence -> verification -> adapt or stop
```

The harness controls retries, time limits, verification, and records. The coding agent is one replaceable component inside that system.

## Requirements

- Python 3.11 or newer
- a project with commands that can verify correctness
- a coding agent that can be invoked non-interactively from a shell command

The harness is provider-agnostic. Your agent command can call a local CLI, an internal wrapper, or a script that talks to an API.

## Install

```bash
python -m pip install -e .
```

## Configure a loop

Copy `examples/python-project.toml` and change four things:

- `project_dir`: the codebase the agent may modify
- `task`: the requested change
- `acceptance_criteria`: the observable definition of done
- `agent_command`: your non-interactive coding-agent command

The command template supports these placeholders:

- `{prompt_file}`: generated Markdown prompt for the current iteration
- `{run_dir}`: audit directory for the entire run
- `{iteration}`: current iteration number

Example:

```toml
[loop]
name = "fix-order-total"
project_dir = "../my-project"
task = """
Correct the order-total calculation so discounts are applied before tax.
Add regression tests for percentage and fixed-value discounts.
"""
acceptance_criteria = [
  "Discounts are applied before tax.",
  "Existing order calculations remain compatible.",
  "Regression tests cover percentage and fixed-value discounts.",
  "All configured verification commands pass.",
]
max_iterations = 4
max_elapsed_seconds = 1200
agent_timeout_seconds = 600
agent_command = "your-agent --prompt-file \"{prompt_file}\""

[[verify]]
name = "tests"
command = "python -m pytest -q"
timeout_seconds = 180

[[verify]]
name = "type-check"
command = "python -m mypy src"
timeout_seconds = 180
```

## Run it

```bash
agent-loop path/to/loop.toml --allow-agent
```

`--allow-agent` is deliberately required because the configured command may edit files and invoke tools.

A successful run exits with code `0`. A failed or bounded run exits with code `1`. Configuration or permission errors exit with code `2`.

## Audit trail

Each run creates a timestamped directory under `.agent-loop/runs/` containing:

```text
config.snapshot.json
iteration-01/
  prompt.md
  agent.json
  verification.json
iteration-02/
  ...
outcome.json
```

This makes the loop inspectable. You can see what the agent received, what it returned, which checks failed, why another iteration occurred, and why the loop stopped.

## How to use this effectively

The quality of a loop is dominated by the quality of its verification. Start by asking: **What evidence would convince a careful human that this task is actually complete?**

Good coding-loop evidence usually combines several layers:

- focused tests for the requested behavior
- the existing test suite for regressions
- a build or compilation check
- static analysis such as linting or type checking
- security or policy checks when the task changes sensitive behavior

Do not use an agent-generated confidence score as the primary verifier. Model judgment can supplement evidence, but it should not replace observable checks when observable checks exist.

See [How to Build an Effective Loop](docs/building-effective-loops.md) for a reusable design method and [Examples](docs/examples.md) for practical configurations.

## Safety model

This project assumes the configured coding agent can modify the target directory. Run it in a Git repository, review changes before committing, restrict the agent's permissions, and avoid exposing production credentials.

The harness enforces iteration and elapsed-time limits. It does not sandbox arbitrary commands. Sandboxing belongs at the environment level, using containers, restricted accounts, disposable worktrees, or another isolation mechanism appropriate to your risk.

## Current scope

Version `0.1.0` intentionally focuses on one reliable pattern:

- one coding agent
- one task
- deterministic command-based verification
- bounded repair attempts
- an inspectable record

It does not pretend that multiple agents, model voting, or elaborate orchestration automatically improve results. Those features should be added only when evaluation shows that they solve a real failure mode.

## Contributing

Contributions are welcome when they preserve the central principle: the loop should stop because evidence satisfies explicit criteria, not because the agent says the work looks complete.

## License

MIT
