# Security

The harness can invoke arbitrary commands configured by the user, and the selected coding agent may edit files or execute tools. Treat configuration files as executable instructions.

Recommended precautions:

- use a disposable Git branch or worktree
- do not expose production credentials
- restrict filesystem and network access
- review diffs before committing
- use containers or another sandbox for untrusted tasks
- require human approval before deployment, deletion, migration, or other irreversible actions

Please report vulnerabilities privately through GitHub's security advisory feature rather than opening a public issue.
