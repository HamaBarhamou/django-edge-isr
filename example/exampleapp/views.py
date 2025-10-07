from django.shortcuts import render, get_object_or_404
from edge_isr import isr, tag
from .models import Post


@isr(tags=lambda req, post_id: [tag("post", post_id)], s_maxage=30, swr=300)
def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related("category"), pk=post_id)
    if post.category_id:
        request._edge_isr_ctx.add_tags([tag("category", post.category_id)])
    return render(request, "post_detail.html", {"post": post})
