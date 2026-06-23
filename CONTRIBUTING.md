# Contributing

Thank you for improving Verifiable Agent Loop.

## Principles

Changes should preserve these properties:

- success is based on configured evidence, not an agent's self-assessment
- retries are bounded
- failures remain inspectable
- provider-specific integrations stay optional
- the default architecture remains understandable
- added complexity addresses a demonstrated failure mode

## Development

```bash
python -m pip install -e .
python -m pip install pytest
pytest -q
```

## Pull requests

Explain the failure mode or use case the change addresses, how it is verified, and any new permissions or risks it introduces.
