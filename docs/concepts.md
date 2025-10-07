
#### `docs/concepts.md`
```markdown
# Concepts

## SWR (Stale-While-Revalidate)
We return cached content immediately (fast TTFB). If the response is stale but within the SWR window, we serve it and trigger a background refresh. Users never wait for recomputation.

## Tags & Tag Graph
- **Tags** are strings like `post:42`, `category:7`.
- The **graph** maintains two sets in Redis:
  - `tag -> {urls}` and `url -> {tags}`.
- On data changes, we resolve impacted URLs by tags and revalidate only those.

## Revalidation
Triggered by signals, management commands, or the API:
1. Resolve URLs by tag(s).
2. Optionally purge those URLs on your CDN.
3. Warm them (HTTP GET with `X-Edge-ISR-Warmup: 1`) to prefill caches.

## Decorator vs Middleware
- **Decorator** applies per-view policy and binds tags (status 200 only).
- **Middleware** provides safe defaults when no decorator policy is present and never overrides explicit headers.
