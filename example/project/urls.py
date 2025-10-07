from django.contrib import admin
from django.urls import path, include
from exampleapp.views import post_detail

urlpatterns = [
    path("admin/", admin.site.urls),
    path("post/<int:post_id>/", post_detail, name="post_detail"),
    path("edge-isr/", include("edge_isr.admin.urls")),
]
