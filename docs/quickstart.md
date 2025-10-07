# Quickstart

## Requirements
- Python 3.10+
- Django 4.2/5.x
- Redis (prod) — tests use fakeredis

## Install
```bash
pip install django-edge-isr
# or dev:
pip install -e ".[dev]"
```

## Settings

```bash
# settings.py
INSTALLED_APPS += ["edge_isr"]
MIDDLEWARE += ["edge_isr.middleware.EdgeISRMiddleware"]

EDGE_ISR = {
  "REDIS_URL": "redis://localhost:6379/0",
  "DEFAULTS": {"s_maxage": 300, "stale_while_revalidate": 3600},
  # Optional queue + CDN:
  # "QUEUE": {"backend": "celery", "queue_name": "edge_isr"},
  # "CDN": {"provider": "cloudflare", "zone_id": "...", "api_token": "..."},
}
```

## Use the decorator

```bash
from edge_isr import isr, tag

@isr(tags=lambda req, post_id: [tag("post", post_id)], s_maxage=300, swr=3600)
def post_detail(request, post_id):
    post = Post.objects.select_related("category").get(pk=post_id)
    request.edge_isr.add_tags([tag("category", post.category_id)])
    return render(request, "post_detail.html", {"post": post})

```

## Hook model changes

```bash
from django.db.models.signals import post_save, post_delete
from edge_isr import revalidate_by_tags, tag

@receiver([post_save, post_delete], sender=Post)
def _post_changed(sender, instance, **kw):
    revalidate_by_tags([tag("post", instance.pk), tag("category", instance.category_id)])
```

## Verify

```bash
curl -I http://localhost:8000/post/1/
# Cache-Control: public, s-maxage=300, stale-while-revalidate=3600
```
