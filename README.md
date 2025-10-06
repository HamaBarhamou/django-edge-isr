# django-edge-isr
**Incremental Static Revalidation for Django** — the speed of static, the freshness of dynamic. Serve fast cached pages from a CDN (or any proxy), while revalidating in the background and regenerating only what changed.

> ⚠️ Status: **Alpha design**. This README describes the vision and the initial MVP. Contributions & feedback welcome.

## Why?
Caching in Django is powerful but hard to keep **fresh**. When content changes, developers either:
- wait for TTLs to expire (stale content), or
- “purge everything” on the CDN (origin stampede), or
- hand‑roll invalidation logic per view/model (fragile).

Modern stacks (e.g. ISR in JS ecosystems) popularized **stale‑while‑revalidate** + **on‑demand revalidation**. `django-edge-isr` brings the same developer experience to Django:

- **SWR semantics** by default (`Cache-Control: s-maxage=..., stale-while-revalidate=...`).
- **Tag-based invalidation**: map pages/partials to the model instances they depend on.
- **On‑demand, targeted revalidation** when data changes (signals).
- **Optional CDN connectors** (Cloudflare/CloudFront) to purge precisely the URLs that changed.
- **Warmup jobs** to repopulate cache in the background and avoid cold starts.

## What you get
- `@isr(...)` **decorator** for views (and template fragments) with tags, TTLs and SWR.
- **Signal handlers** that listen to `post_save` / `post_delete` and trigger revalidation.
- **Tag graph** stored in Redis to know which URLs depend on which objects.
- **Connectors** for Cloudflare / CloudFront (opt‑in).
- **Admin UI** (preview) to see cached URLs, tags, and revalidation status.
- **Queue adapters** (Celery/RQ or an in‑process fallback) for warmups & revalidation tasks.

## Quickstart (MVP sketch)
```python
# settings.py
INSTALLED_APPS += ["edge_isr"]
EDGE_ISR = {
    "REDIS_URL": "redis://localhost:6379/0",
    "CDN": {"provider": "cloudflare", "zone_id": "...", "api_token": "..."},
    "DEFAULTS": {"s_maxage": 300, "stale_while_revalidate": 3600},
}
```

```python
# urls.py
from edge_isr import isr, tag

@isr(tags=lambda req, post_id: [tag("post", post_id)], s_maxage=300, swr=3600)
def post_detail(request, post_id):
    post = Post.objects.select_related("category").get(pk=post_id)
    # Optionally add more tags dynamically
    request.edge_isr.add_tags([tag("category", post.category_id)])
    return render(request, "post_detail.html", {"post": post})
```

```python
# models.py
from django.db.models.signals import post_save, post_delete
from edge_isr import revalidate_by_tags, tag

@receiver([post_save, post_delete], sender=Post)
def _post_changed(sender, instance, **kw):
    revalidate_by_tags([tag("post", instance.pk), tag("category", instance.category_id)])
```

**That’s it**: on each `Post` change, the package purges just the affected URLs on your CDN, serves the **stale** page immediately (SWR), and warms a fresh version in the background.

## Concepts
- **Tags**: strings like `post:42`, `category:7`. Views/fragments declare which tags they depend on.
- **Tag Graph**: Redis sets keep two maps: `tag -> {urls}` and `url -> {tags}`.
- **Revalidation**: on data change, determine URLs by tags, purge them at CDN (optional), and **warm** them by fetching from the origin with a special header (so they’re rebuilt & cached for the next visitor).
- **SWR headers**: responses include `Cache-Control: s-maxage=N, stale-while-revalidate=M` (and `ETag` when appropriate).

## Supported (planned for 0.x series)
- **Python**: 3.10+
- **Django**: 4.2, 5.x
- **Cache store**: Redis (for tag graph & job state)
- **Task queue**: Celery or RQ (recommended); in‑process fallback for dev
- **CDN connectors**: Cloudflare (0.1), CloudFront (0.2). Works without a CDN too (reverse proxy or just Django cache).

## When NOT to use it
- Highly personalized or private pages (vary by cookie/user). Use fine‑grained keys or bypass ISR for those routes.
- Endpoints with non‑idempotent side effects.

## Roadmap
- **v0.1**: SWR headers, manual tags, Redis tag graph, Cloudflare purge, warmup worker, basic admin.
- **v0.2**: CloudFront invalidations, automatic tag enrichment helpers, template‑fragment decorator.
- **v0.3**: Admin UX, metrics, per‑locale/device cache keys, smarter warmup (rate‑limiting, batching).

## FAQ
**Q:** Do I need a CDN?  
**A:** No. You can start locally or behind Nginx/Varnish. CDNs unlock global edge caching and instant purges.

**Q:** How does it avoid origin stampede?  
**A:** SWR serves the stale version while revalidating **once** in the background; warmups are enqueued & throttled.

**Q:** How do I tag template fragments?  
**A:** Use `@isr_fragment` (0.2) or `{% isrcache 'fragment', tags=['category:7'] %}` in templates.

## Contributing
Issues and PRs welcome. Please include a minimal repro (view, tags used, and the observed cache headers).

## License
MIT
