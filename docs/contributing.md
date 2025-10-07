# Contributing

## Dev Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
redis-server  # or fakeredis in tests
```

## Run tests

```bash
python -m pytest -q
```

## Style

- Ruff for linting (ruff check .)

- Keep functions small and tested.

- Add/extend docs for new features.

## Good First Issues

- Add CloudFront connector tests

- Fragment caching decorator (`@isr_fragment`)

- Prometheus metrics exporter
