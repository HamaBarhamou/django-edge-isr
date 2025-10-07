
#### `docs/deployment.md`
```markdown
# Deployment

## With a CDN (recommended)
- Enable caching for HTML at the edge.
- Respect origin `Cache-Control` headers.
- Allow `stale-while-revalidate`.
- Use precise URL purge/invalidation APIs.

## Without a CDN
- Reverse proxy (Varnish/Nginx) or just Django's cache.
- You still get SWR behavior and warmups.

## Gotchas
- Don’t decorate private/personalized pages.
- Use `Vary` helpers for locale/device if needed.
- Keep Redis close to your app (latency matters).
