# django-edge-isr — MVP Architecture & Release Plan

This document details the technical architecture of the MVP, the modules, the CDN connectors, the tag graph, warmup tasks, and a 3-step release plan.

---

## 1. High-level flow

```
Browser → CDN/Proxy (Cloudflare/CloudFront/Varnish)
          │ (serves cached; if stale → revalidate in background)
          ▼
        Django origin
          │
       edge_isr: view decorator sets SWR headers + records URL↔tags
          │
          ├─► Redis: tag graph (url↔tags) + job state
          ├─► Queue: revalidation/warmup jobs (Celery/RQ)
          └─► Connectors: purge CDN for affected URLs
```

- **Serve**: CDN serves cached response immediately if fresh. If stale within SWR window, it still serves it and triggers revalidation.
- **Revalidate**: Worker warms the URL by fetching it from origin with a special header (`X-Edge-ISR-Warmup: 1`) so middleware bypasses SWR, recomputes the view, stores mapping (tags↔url) and returns new headers for CDN to cache.
- **Purge**: On data change, only affected URLs are purged (not the whole site).

---

## 2. Modules

```
edge_isr/
  __init__.py
  settings.py                # typed settings + defaults
  policy.py                  # SWR / Cache-Control / ETag helpers
  decorators.py              # @isr, @isr_fragment
  context.py                 # request-scoped tag collector (request.edge_isr.add_tags())
  tags.py                    # Tag model (string), helpers, validators
  graph.py                   # Redis-backed TagGraph: url↔tags sets
  signals.py                 # helpers for post_save/post_delete → revalidate_by_tags()
  revalidate/
    queue.py                 # adapters: Celery/RQ/InProcess
    tasks.py                 # warmup_url(url), revalidate_by_tags(tags)
  connectors/
    base.py                  # interface (purge_urls(urls))
    cloudflare.py            # CF API client (purge by URL, batching, rate limits)
    cloudfront.py            # AWS boto3 invalidations (paths, batching)
  admin/
    views.py, urls.py        # dashboard: URLs by tag, purge, job status
  middleware.py              # capture URL, set headers, honor warmup header
  instrumentation.py         # logging, counters, timing
  utils.py                   # signing, url normalization, key builders
```

### 2.1 `@isr` decorator (views & fragments)
- Accepts: `tags`, `s_maxage`, `swr`, optional `vary`, optional custom cache key builder.
- Stores `url → {tags}` and `tag → {urls}` in Redis (two sets).
- Adds response headers: `Cache-Control: public, s-maxage=N, stale-while-revalidate=M` (+ `ETag` when available).

### 2.2 Tag graph (Redis)
- Keys:
  - `edgeisr:url:{sha}` → Set of tags
  - `edgeisr:tag:{tag}` → Set of urls
- Operations:
  - `bind(url, tags)`; `unbind(url)`; `urls_for(tags)`; `tags_for(url)`
- TTL policy:
  - Tag graph entries TTL matched to `swr + margin`; refreshed on each warmup.

### 2.3 Revalidation pipeline
1. **Trigger**: `revalidate_by_tags([tag("post", 42)])`
2. **Resolve** URLs: `urls = graph.urls_for(tags)`
3. **Purge**: connectors purge these URLs at the CDN (optional if CDN not configured).
4. **Warm**: enqueue `warmup_url(url)` to prefill CDN/origin cache.
5. **Throttle**: batch size + backoff to protect origin.

### 2.4 Warmup job (`warmup_url`)
- Makes a GET to the origin with `X-Edge-ISR-Warmup: 1`.
- Middleware bypasses SWR and ensures fresh render.
- On success: updates ETag/headers; rebinds tags; records metrics.

### 2.5 Middleware
- Adds default SWR headers if decorator not used but policy configured.
- Honors `X-Edge-ISR-Warmup` to force compute-and-store.
- Optionally sets `Surrogate-Key: tag1 tag2 ...` header (for CDNs that support key-based purge later).

---

## 3. CDN connectors

### 3.1 Cloudflare
- Auth: API Token (scoped to cache purge).
- Endpoint: purge-by-URL in batches (<=30 URLs typical).
- Extras: supports SWR and stale-if-error at the edge; can rely on Cache Rules.

### 3.2 CloudFront
- Auth: AWS credentials (with `cloudfront:CreateInvalidation`).
- Invalidation: create invalidation with the list of paths (`/path/*` or concrete URLs).
- Batching & rate-limiting: respect CloudFront quotas; aggregate by distribution.

Both connectors are **optional**; without them, use only SWR + origin cache (or purge via reverse proxy).

---

## 4. Configuration

```python
EDGE_ISR = {
  "REDIS_URL": "redis://localhost:6379/0",
  "CDN": {
    "provider": "cloudflare",
    "zone_id": "...",
    "api_token": "...",
    # or:
    # "provider": "cloudfront",
    # "distribution_id": "E123...",
    # "aws_access_key_id": "...",
    # "aws_secret_access_key": "...",
    # "aws_region": "us-east-1",
  },
  "DEFAULTS": {"s_maxage": 300, "stale_while_revalidate": 3600},
  "QUEUE": {"backend": "celery", "queue_name": "edge_isr"},
}
```

---

## 5. Data model & keys

- **URL key**: normalized (scheme+host+path+query filtered by allowlist). Hash to avoid giant Redis keys.
- **Tags**: developer-defined, normalized (`lowercase`, `:` separator).
- **Versioning**: include an optional `build-id` pseudo-tag to invalidate groups at once.

---

## 6. Observability & Admin

- **Dashboard**: search by tag or URL, see last warmup, purge now, replay.
- **Metrics**: revalidations/hour, warmup latency, purge latency, hit ratio (if backend provides).

---

## 7. Security & correctness

- Don’t ISR **private** endpoints; require explicit opt‑in (`@isr`).
- Respect `Vary` headers (locale, device, cookie). Provide helpers for common cases.
- Prevent revalidation loops (idempotent warmup, dedupe inflight jobs).

---

## 8. Testing strategy

- Unit tests for tag graph, decorators, policy headers.
- Integration tests with a fake CDN client.
- E2E docker-compose (Django + Redis + Celery) running a tiny demo app.

---

## 9. Release plan (3 steps)

### v0.1 — “SWR & Cloudflare” (2–3 weeks)
- `@isr` decorator + Redis tag graph + SWR headers
- Cloudflare purge connector + warmup worker (Celery) + basic admin
- Docs + example project

### v0.2 — “CloudFront & Fragments”
- CloudFront invalidation connector
- Template-fragment decorator / templatetag
- Auto‑tagging helpers (e.g., from queryset/model instances)

### v0.3 — “Nice UX & Metrics”
- Admin improvements (filters, batch actions), Prometheus exporters
- Rate‑limited, prioritized queue; better per‑tenant cache keys
- Recipes for HTMX/DRF/Wagtail

---

## 10. Open questions / future ideas
- Support **Surrogate Keys** natively on CDNs that provide them.
- Heuristic auto‑tagging by inspecting context (opt‑in).
- Support for ESI/fragment ISR (edge‑side includes) on capable proxies.
- Per‑locale/device variants (Accept-Language, UA hints) with helpers.
