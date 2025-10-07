# django-edge-isr

**Incremental Static Revalidation for Django** — CDN-grade performance with fresh data.
Serve cached pages fast and revalidate in the background when content changes, targeting only affected URLs.

> Status: **Alpha**. We’re building out the 0.x series with safety rails and docs.

## Highlights
- **SWR semantics**: `Cache-Control: s-maxage=N, stale-while-revalidate=M`
- **Tag-based invalidation** across pages & fragments
- **On-demand revalidation** via signals/commands
- **Optional CDN connectors**: Cloudflare (0.1), CloudFront (0.2)
- **Warmup jobs** to prefill caches and avoid stampede
- **Admin JSON endpoints** to inspect tags → URLs

Jump to: [Quickstart](quickstart.md) · [Concepts](concepts.md) · [API](api.md)
