
# Changelog

All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog**, and this project adheres to **Semantic Versioning** (as much as possible for a 0.x series).

## [Unreleased]

### Added
- Release guide (`docs/release.md`).
- Tests: ensure `Vary` headers are **merged** (existing `Vary` + decorator `vary=[]`).
- Tests: **no binding** occurs when a view returns **non-200**.

### Changed
- README: clearer install & docs links.

### Fixed
- Avoid Jekyll/Liquid pitfalls in README (no Liquid tags).

---

## [0.0.7] – 2025-10-08

### Added
- First public **PyPI** release (`pip install django-edge-isr`).

### Fixed
- Packaging metadata & CI release workflow adjustments.

---

## [0.0.6] – 2025-10-07

### Fixed
- CI release pipeline refinements (artifact handling, metadata checks).

---

## [0.0.5] – 2025-10-07

### Changed
- Version bump & minor workflow tweaks.

---

## [0.0.4] – 2025-10-07

### Fixed
- Release workflow fixes (split build/publish, gating via `PUBLISH_TO_PYPI`).

---

## [0.0.3] – 2025-10-07

### Added
- GitHub Pages docs publishing.

---

## [0.0.1] – 2025-10-06

### Added
- MVP: `@isr` decorator, middleware (SWR headers), tag graph (Redis), revalidation tasks (purge + warmup), admin endpoints.
- Basic tests for headers, tag binding, revalidation flow.
