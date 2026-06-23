# Examples

These examples show how the same control loop changes when the task and risk change.

## Bug fix

Task:

> Fix a parser that drops the final CSV field when the line has no trailing newline.

Useful verification:

```toml
[[verify]]
name = "focused-regression"
command = "python -m pytest tests/test_csv_parser.py -q"

[[verify]]
name = "full-suite"
command = "python -m pytest -q"

[[verify]]
name = "type-check"
command = "python -m mypy src"
```

The focused test proves the requested behavior. The full suite checks regressions. The type check catches interface damage.

## Front-end component

Task:

> Add keyboard navigation to the account menu without changing pointer behavior.

Useful verification:

```toml
[[verify]]
name = "component-tests"
command = "npm test -- --run account-menu"

[[verify]]
name = "lint"
command = "npm run lint"

[[verify]]
name = "build"
command = "npm run build"
```

Accessibility may also require a human or browser-based review. The loop should report that as an approval requirement rather than pretending a build proves usability.

## Dependency update

Task:

> Upgrade a dependency to address a published vulnerability without introducing breaking API changes.

Useful verification:

```toml
[[verify]]
name = "tests"
command = "npm test"

[[verify]]
name = "build"
command = "npm run build"

[[verify]]
name = "audit"
command = "npm audit --audit-level=high"
```

A passing audit does not prove every security concern is resolved, but it is relevant evidence for the stated vulnerability objective.

## Refactor

Task:

> Extract invoice-tax calculation into a dedicated module without changing observable behavior.

Useful verification:

```toml
[[verify]]
name = "characterization-tests"
command = "python -m pytest tests/test_invoice_totals.py -q"

[[verify]]
name = "full-suite"
command = "python -m pytest -q"
```

For a behavior-preserving refactor, the acceptance criteria should emphasize unchanged outputs rather than subjective elegance.

## A weak loop transformed

Weak:

> Review the project, improve the checkout, test your work, and keep trying until it is good.

Stronger:

> Correct checkout so a case-only product cannot be purchased in quantities that are not multiples of its case size. Preserve existing cart behavior for all other products. Add regression tests for valid and invalid quantities. Stop only when the focused checkout tests, full test suite, and production build pass. Stop unsuccessfully after four attempts or twenty minutes.

The stronger version defines behavior, non-regression requirements, evidence, and boundaries.
