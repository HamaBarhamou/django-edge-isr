from django.contrib import admin
from django.urls import path, include
from .views import (
    basic_view,
    decorated_post,
    vary_view,
    vary_merge_view,
    non_200_view,
    no_tags_view,
    vary_dedupe_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("basic/", basic_view),
    path("post/<int:pid>/", decorated_post),
    path("vary/", vary_view),
    path("edge-isr/", include("edge_isr.admin.urls")),
    path("vary-merge/", vary_merge_view),
    path("non200/", non_200_view),
    path("no-tags/", no_tags_view),
    path("vary-dedupe/", vary_dedupe_view),
]
