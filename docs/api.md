# API Reference

## Decorators
### `isr(tags=None, s_maxage=300, swr=3600, vary=None)`
- `tags`: `callable(request, *args, **kwargs) -> Iterable[str]`
- `s_maxage`: seconds for CDN/shared caches
- `swr`: seconds for `stale-while-revalidate`
- `vary`: iterable of header names to merge into `Vary`

## Request Context
- `request.edge_isr.add_tags(iterable_of_tags)`

## Helpers
- `tag(namespace, id_or_str) -> str` → `"namespace:id"`

## Tag Graph (`edge_isr.graph`)
- `bind(url, tags)`
- `unbind(url)`
- `urls_for(tags) -> list[str]`
- `tags_for(url) -> list[str]`

## Revalidation (`edge_isr.revalidate.tasks`)
- `revalidate_by_tags(tags) -> list[str]` (returns URLs)
- `warmup_url(url)`

## Settings (`EDGE_ISR`)
```python
EDGE_ISR = {
  "REDIS_URL": "...",
  "DEFAULTS": {"s_maxage": 300, "stale_while_revalidate": 3600},
  "QUEUE": {"backend": "inline|celery|rq", "queue_name": "edge_isr"},
  "CDN": {...},  # cloudflare | cloudfront
}
