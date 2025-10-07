# Revalidation Pipeline

## Flow
1. Change detected (signal, command, or manual call).
2. `urls = urls_for(tags)`
3. Purge URLs on CDN (optional).
4. `warmup_url(url)` enqueued per URL.

## Warmup
- Sends `GET <url>` with header `X-Edge-ISR-Warmup: 1`.
- Middleware/View recomputes and updates headers/graph.

## Queues
- `inline` (dev), `celery`, `rq`. Configure via `EDGE_ISR["QUEUE"]`.

## Commands
```bash
python manage.py revalidate_tags post:42 category:7
python manage.py warm_url https://example.com/post/42/
