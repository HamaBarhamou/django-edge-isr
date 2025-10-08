# Release guide

This guide explains how to publish a new version to **PyPI** using **GitHub Actions**.

## TL;DR

1. Bump the version in `pyproject.toml`.
2. Open a PR from `develop` → `main`, let CI pass, then merge.
3. Create an annotated tag `vX.Y.Z` on `main` and push it.
4. The `release.yml` workflow builds wheels/sdist, runs `twine check`, and uploads to PyPI.
5. Verify the release: `pip install django-edge-isr==X.Y.Z`.

---

## Prerequisites

- Repository variable **`PUBLISH_TO_PYPI`** set to **`true`**
  _Settings → Secrets and variables → **Variables** → Add `PUBLISH_TO_PYPI=true`._
- Repository secret **`PYPI_API_TOKEN`** configured
  _Settings → Secrets and variables → **Secrets** → Add `PYPI_API_TOKEN` (a `pypi-...` token)._
- Workflow file **`.github/workflows/release.yml`** present (build + `twine` upload).
- Branch protections set as you like (e.g., enforce PRs to `main`, no merge commits).

---

## Steps

### 1) Bump the version

Edit `pyproject.toml`:

```toml
[project]
version = "X.Y.Z"
````

Commit on `develop`.

### 2) Open PR to `main`

* Open a PR: `develop` → `main`.
* Wait for all CI checks (lint/tests/docs) to pass.
* Merge the PR (recommended: **Squash and merge** or **Rebase and merge** if merge commits are blocked).

### 3) Tag the release

Create a tag **on `main`** that matches the version:

```bash
git switch main
git pull
git tag vX.Y.Z -m "Release X.Y.Z"
git push origin vX.Y.Z
```

The `release.yml` workflow is triggered by tags matching `v*.*.*`.

### 4) What the workflow does

* Checks that `pyproject.toml` version matches the tag.
* Builds **sdist** and **wheel** (`python -m build`).
* Runs `twine check dist/*` to validate metadata.
* Uploads to **PyPI** using the `PYPI_API_TOKEN`.

### 5) Verify the release

In a clean virtualenv:

```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install django-edge-isr==X.Y.Z
python -c "import edge_isr; print(edge_isr.__version__)"
```

Also verify the docs site:
**[https://hamabarhamou.github.io/django-edge-isr/](https://hamabarhamou.github.io/django-edge-isr/)**

---

## (Optional) TestPyPI dry-run

If you want to test packaging before the public release:

```bash
python -m build
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# then test install:
pip install -i https://test.pypi.org/simple/ django-edge-isr==X.Y.Z
```

You’ll need a **TestPyPI** token if you go that route.

---

## Troubleshooting

* **Version mismatch (workflow fails early):** Ensure the tag `vX.Y.Z` matches `[project].version` in `pyproject.toml`.
* **“InvalidDistribution: Metadata is missing required fields”**:
  Remove old `dist/`, rebuild locally with `python -m build`, run `python -m twine check dist/*` to catch issues before pushing a tag.
* **“File already exists”** on PyPI: You pushed the same version twice. Bump the version and re-tag.
* **CI doesn’t publish:** Check that `PUBLISH_TO_PYPI=true` (variable), the secret `PYPI_API_TOKEN` is set, and the tag pattern matches `v*.*.*`.
