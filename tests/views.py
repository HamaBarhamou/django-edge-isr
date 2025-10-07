from django.http import HttpResponse
from edge_isr import isr, tag

def basic_view(request):
    return HttpResponse("ok")

@isr(tags=lambda req, pid: [tag("post", pid)], s_maxage=30, swr=300)
def decorated_post(request, pid: int):
    return HttpResponse(f"post {pid}")

@isr(tags=lambda req: ["vary:test"], s_maxage=10, swr=100, vary=["Accept-Language"])
def vary_view(request):
    return HttpResponse("vary")

@isr(vary=["Accept-Language"])
def vary_merge_view(request):
    r = HttpResponse("vary-merge")
    r["Vary"] = "User-Agent"
    return r

@isr(tags=lambda req: ["non200:test"], s_maxage=10, swr=100)
def non_200_view(request):
    return HttpResponse("nope", status=404)