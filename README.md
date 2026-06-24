# Agent Loop for Vibe Coders

A guided coding-agent loop that lets Claude Code or Codex work on one project, checks the result, and retries only when the checks fail.

## What this tool is

This repository does **not** contain an AI model.

It connects four things:

- **Claude Code or Codex** does the coding work.
- **This agent loop** supervises the attempts.
- **Your coding project** is the folder the AI may change.
- **Tests, builds, linting, or type checks** provide evidence that the work is complete.

Think of the AI coding agent as the worker and this loop as the supervisor.

## Start here

Follow these steps in order. No prior experience with agent loops is required.

### 1. Confirm Python 3.11 or newer

Open PowerShell and run:

```powershell
python --version
```

You should see Python 3.11 or newer. On Windows, this also works when multiple Python versions are installed:

```powershell
py -3.14 --version
```

### 2. Confirm that you have an AI coding agent

You need **one** of these installed and signed in.

For Claude Code:

```powershell
claude --version
```

For Codex CLI:

```powershell
codex --version
```

If neither command works, install and sign in to Claude Code or Codex before continuing.

### 3. Choose a safe test project

Choose a **separate coding project** that you are willing to let an AI agent modify.

The project should:

- already be a Git repository
- have tests, a build command, linting, type checks, or Python files that can be compiled
- not contain irreplaceable uncommitted work

Do not use this agent-loop repository itself as the test project.

### 4. Download this repository

Download the ZIP from GitHub and extract it, or clone the repository.

Open PowerShell inside the extracted agent-loop folder.

### 5. Install the agent-loop command

Run:

```powershell
python -m pip install -e .
```

If you installed a newer Python alongside an older one, use that version explicitly. Example:

```powershell
py -3.14 -m pip install -e .
```

Confirm the installation:

```powershell
agent-loop --help
```

You may now run `agent-loop` from any folder on your computer.

### 6. Start the guided setup

Run:

```powershell
agent-loop start
```

The tool will walk you through five steps:

1. choose Claude Code or Codex
2. approve one version-check command
3. enter the full path to the separate coding project the AI may modify
4. describe one coding task and what success looks like
5. review the detected verification checks and approve the final setup

The tool does not search your computer for an AI agent. You choose the agent, and it asks permission before running that agent's version command.

### 7. Review before anything runs

The tool shows a final summary containing:

- the AI coding agent
- the exact project folder it may modify
- the task
- the success condition
- the verification commands
- the retry limit

You must type `CREATE` to save the loop and then type `RUN` before the AI agent starts editing files.

### 8. Read the result

At the end, the terminal tells you:

- whether the checks passed
- why the loop stopped
- how many attempts were used
- where the detailed audit record was saved

Every run is recorded under `.agent-loop/runs/`.

## What the loop does during a run

The loop follows this process:

```text
clear task -> AI agent makes changes -> independent checks run -> retry or stop
```

The AI agent does not get to declare its own work complete. The configured tests, build, lint, type-check, compile, or Git checks determine whether the loop passes.

## Safety rules

Use a Git repository and commit or back up important work before running the loop. The selected AI coding agent may edit files and execute coding tools inside the project folder you approve.

The guided setup refuses to continue when:

- the selected coding agent cannot be confirmed
- the chosen project folder does not exist
- the project is not a Git repository
- no trustworthy verification command can be found

## Important clarification

A loop is not effective on its own. It becomes effective only when its goal, tools, evidence, acceptance criteria, limits, and human controls match the task.

This project focuses on coding because software work often has objective evidence: tests, builds, linters, type checks, and observable file changes.

## Advanced use

The guided setup creates `.agent-loop/quick-start.toml` inside the selected coding project. Experienced users can edit that file or create their own configuration.

Run an existing configuration with:

```powershell
agent-loop run path\to\loop.toml --allow-agent
```

See [How to Build an Effective Loop](docs/building-effective-loops.md) and [Examples](docs/examples.md).

## License

MIT
