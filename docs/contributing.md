# Contributing

Thanks for your interest in **django-edge-isr**! This document explains how to set up your dev environment, run tests, follow our style guides, and open high-quality pull requests.

---

## Table of contents

- [Getting started](#getting-started)
- [Project layout](#project-layout)
- [Run the example app](#run-the-example-app)
- [Testing](#testing)
- [Linting & formatting](#linting--formatting)
- [Pre-commit hooks](#pre-commit-hooks)
- [Git & PR conventions](#git--pr-conventions)
- [Design guidelines](#design-guidelines)
- [Performance & safety checks](#performance--safety-checks)
- [Good first issues](#good-first-issues)
- [Opening issues](#opening-issues)
- [Security](#security)
- [License](#license)

---

## Getting started

```bash
# 1) Create & activate virtualenv
python -m venv .venv
source .venv/bin/activate

# 2) Install in editable mode with dev extras
pip install -e ".[dev]"

# 3) Optional: start a local Redis (tests use fakeredis by default)
redis-server  # (optional)
```

> We support Python **3.10+** and Django **4.2 / 5.x** in the 0.x series.



## Project layout

```bash
├─ src/edge_isr/         # package code
│  ├─ connectors/        # CDN connectors (cloudflare, cloudfront)
│  ├─ revalidate/        # queue adapters + tasks
│  ├─ admin/             # minimal admin endpoints (JSON)
│  ├─ middleware.py      # default SWR policy + tag binding
│  ├─ decorators.py      # @isr(...) for views/fragments
│  └─ ...
├─ tests/                # pytest + pytest-django (in-memory DB)
│  ├─ django_settings.py # isolated settings for tests
│  ├─ urls.py, views.py  # tiny test endpoints
│  └─ ...                # unit & integration tests
├─ example/              # demo Django project (manual e2e)
├─ docs/                 # documentation sources
└─ pyproject.toml        # build + tooling config
```

---

## Run the example app

The `example/` project helps you test the package manually:

```bash
cd example
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Visit http://127.0.0.1:8000/post/1/ (see README for quick steps)
```

---

## Testing

We use **pytest** + **pytest-django**. Tests are isolated from your system Redis via **fakeredis**.

* Run the full suite:

```bash
python -m pytest -q
```

* Run a subset:

```bash
python -m pytest tests/test_graph.py::test_bind_and_urls_for -q
```

* Useful envs:

```bash
# show prints/logs on failure
pytest -q -s
# stop on first failure
pytest -q -x
```

### Writing tests

* Place tests in `tests/` and import the package as `edge_isr`.
* If you need Redis, **don’t** hit a real server — use the already-configured `fakeredis` fixture (`tests/conftest.py` patches `edge_isr.graph.redis.from_url` automatically).
* HTTP tests can use Django’s `client` fixture.
* Prefer small, focused tests; add one failing test per bug before fixing it.

Minimal example:

```py
# tests/test_my_feature.py
from edge_isr import tag, graph

def test_something():
    url = "http://testserver/x/"
    t = tag("post", 123)
    graph.bind(url, [t])
    assert url in graph.urls_for([t])
```

---

## Linting & formatting

We follow the common Python toolchain:

* **Black** – the **only** formatter (opinionated, deterministic).
* **Ruff** – linter (fast, catches style & small logic mistakes). We use `ruff --fix` for safe auto-fixes, **not** for formatting.

Run locally:

```bash
# format
black .

# lint
ruff check .
# or apply safe auto-fixes:
ruff check . --fix
```

Black & Ruff settings live in `pyproject.toml` (`[tool.black]`, `[tool.ruff]`).

---

## Pre-commit hooks

We recommend installing **pre-commit** to run Black/Ruff and basic hygiene checks before every commit.

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

`.pre-commit-config.yaml` includes:

* `end-of-file-fixer`, `trailing-whitespace`, `check-yaml`, `check-toml`, `debug-statements`
* **Black**
* **Ruff** (lint only; no ruff-format)

---

## Git & PR conventions

* **Branching**: open feature/bug branches off `develop` (e.g. `feat/connector-cloudfront`, `fix/tag-ttl`).
* **Commits**: use [Conventional Commits](https://www.conventionalcommits.org/):

  * `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`…
* **PR checklist**:

  * [ ] Title uses Conventional Commits
  * [ ] Tests added/updated and pass locally (`pytest -q`)
  * [ ] Lint & format pass (`pre-commit run --all-files`)
  * [ ] Docs updated (`README`, `docs/`, examples if applicable)
  * [ ] No breaking changes unless explicitly discussed

Small, focused PRs are merged faster than “mega PRs”.

---

## Design guidelines

* **Opt-in**: ISR is explicit (`@isr`) — never cache private/personalized endpoints by default.
* **Headers first**: SWR semantics via `Cache-Control: s-maxage=..., stale-while-revalidate=...`.
* **Tag graph is the source of truth**: always bind `url ↔ tags` for targeted invalidations.
* **Connectors are optional**: package must work without Cloudflare/CloudFront (reverse proxy or just origin cache).
* **Safe-by-default**: no infinite loops (idempotent warmups), respect `Vary`, handle non-200 responses gracefully.
* **DX matters**: clear errors, good defaults, minimal boilerplate.

---

## Performance & safety checks

* Avoid origin stampede:

  * serve stale within SWR window, revalidate **once** in background
  * queue warmups and throttle them
* Keep Redis keys small (we hash long URL keys internally).
* Don’t bind on non-200 responses; don’t purge on empty resolution sets.
* Add tests around headers, `Vary`, and tag resolution for new features.

---

## Good first issues

* **Connector coverage**: add more tests for CloudFront invalidations (batching, quotas).
* **Fragment caching**: prototype `@isr_fragment` / `{% isrcache %}` with a tiny API and tests.
* **Admin UX**: filters, pagination, and simple replay actions in `edge_isr.admin`.
* **Metrics**: Prometheus exporter (warmup latency, purge latency, hit ratio if available).
* **Docs**: short “recipes” for Django REST Framework, HTMX, Wagtail.

If you’re unsure where to start, comment on an issue and we’ll help you scope it.

---

## Opening issues

Please include:

* Environment (Python/Django versions), package version/commit
* Minimal reproduction (view/model snippet, headers observed)
* Expected vs. actual behavior
* Logs/tracebacks (trim to essentials)

Bug reports with a failing test case are ❤️.

---

## Security

If you believe you’ve found a security issue, **do not** open a public issue. Please email the maintainers privately: **[hamabarhamou@gmail.com](mailto:hamabarhamou@gmail.com)**. We’ll respond quickly and coordinate a fix.

---

## License

By contributing, you agree that your contributions are licensed under the project’s **MIT** license.
