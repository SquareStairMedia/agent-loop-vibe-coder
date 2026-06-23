# How to Build an Effective Loop

The reusable part of an agent loop is its control structure. The effective part is specific to the task.

## The seven-part loop design

### 1. Objective

Describe the desired end state, not just the next action.

Weak:

> Improve this code.

Strong:

> Ensure duplicate webhook deliveries do not create duplicate invoices, while preserving existing successful invoice creation behavior.

### 2. State

Give the loop access to the state it must inspect: source files, repository history, test failures, tool output, requirements, and prior attempts. Do not repeatedly send the entire world. Preserve relevant state and update it deliberately.

### 3. Action

Define what the agent is permitted to do. For coding work, that may include reading files, editing code, adding tests, and running approved development tools. Avoid granting permissions unrelated to the task.

### 4. Evidence

Identify outputs that exist independently of the agent's opinion. Examples include test results, compiler output, generated artifacts, schema validation, benchmark measurements, and reproducible command output.

### 5. Verification

Convert acceptance criteria into checks. Verification should answer a narrow question: did the observable result satisfy the required condition?

Prefer deterministic checks when possible. Use model-based review only for qualities that cannot be reduced to deterministic evidence, and make its rubric explicit.

### 6. Adaptation

Feed useful failure information into the next attempt. A repair loop should receive failed check names, command output, and relevant diagnostics. It should not blindly repeat the original prompt.

### 7. Boundaries

Every loop needs explicit stopping and escalation rules:

- maximum iterations
- elapsed-time limit
- per-command timeout
- cost or token limit when available
- permission boundaries
- approval before irreversible actions
- a clear failure outcome

A loop that cannot fail safely is not autonomous; it is uncontrolled.

## Designing acceptance criteria

Acceptance criteria should be observable, necessary, and difficult to game.

Weak criteria:

- code is high quality
- solution is elegant
- agent is confident

Stronger criteria:

- the new endpoint returns `409` for an existing idempotency key
- the regression test fails before the fix and passes after it
- the full test suite passes
- the application builds with warnings treated as errors
- no database migration removes or renames an existing column

Not every criterion must be automated, but every criterion should identify what evidence a human or machine would inspect.

## Match verification to risk

Low-risk formatting change:

- formatter
- focused snapshot test

Business-logic change:

- focused regression tests
- full test suite
- type check

Authentication change:

- focused positive and negative tests
- full test suite
- static security checks
- mandatory human review

Database migration:

- migration validation
- rollback test
- compatibility check
- mandatory human approval before production execution

The same loop engine can coordinate each example. The verification and authority boundaries must differ.

## Common failure modes

### Self-verification

The writer says the work is complete because it appears correct. Replace this with external tests and observable evidence.

### Vague completion conditions

The loop keeps polishing because “better” has no endpoint. Define a measurable end state.

### Repeating without learning

Each iteration receives the original task but not the failed evidence. Feed back the actual diagnostics.

### Verification gaming

The agent changes tests or configuration to remove the failure rather than fixing the behavior. State this prohibition explicitly and review verifier changes carefully.

### Endless retries

The same strategy fails repeatedly. Set limits and preserve a failure report for human diagnosis.

### Excessive architecture

Multiple agents and reviewers are added before the basic loop has an evaluation. Start with the simplest loop that can be measured.

## When model-based verification is appropriate

Some outcomes involve qualities such as clarity, tone, visual coherence, or completeness of an explanation. A model-based evaluator can help, but it should use:

- a written rubric
- isolated context
- evidence citations
- structured scoring
- a minimum passing threshold
- calibration against human-reviewed examples
- deterministic checks alongside it

Model-based evaluation is evidence with uncertainty, not objective truth.

## A practical design test

Before running a loop, be able to complete this sentence:

> The loop will stop successfully when ______ produces ______ evidence, and it will stop unsuccessfully when ______.

If the blanks are vague, the loop is not ready.
