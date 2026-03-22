from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.http import JsonResponse

from catalog.models import Mineral
from pages.models import RecognitionHistory


def home(request):
    return render(request, "pages/home.html")


def about(request):
    return render(request, "pages/about.html")


def tours(request):
    return render(request, "pages/tours.html")


def collection(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("type", "").strip()

    minerals = Mineral.objects.all()

    if query:
        minerals = minerals.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(formula__icontains=query) |
            Q(color__icontains=query)
        )

    if category:
        minerals = minerals.filter(category=category)

    return render(request, "pages/collection.html", {
        "minerals": minerals,
        "query": query,
        "category": category,
    })


def mineral_detail(request, slug):
    mineral = get_object_or_404(Mineral, slug=slug)
    return render(request, "pages/mineral_detail.html", {
        "mineral": mineral,
    })


def map_view(request):
    return render(request, "pages/map.html")


def statistics_view(request):
    total_recognitions = RecognitionHistory.objects.count()
    upload_count = RecognitionHistory.objects.filter(source="upload").count()
    camera_count = RecognitionHistory.objects.filter(source="camera").count()

    top_minerals_qs = (
        RecognitionHistory.objects
        .exclude(top1_label="")
        .values("top1_label")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    top_minerals = list(top_minerals_qs)

    latest_recognitions = RecognitionHistory.objects.select_related(
        "user",
        "predicted_mineral",
    ).order_by("-created_at")[:8]

    return render(request, "pages/statistics.html", {
        "total_recognitions": total_recognitions,
        "upload_count": upload_count,
        "camera_count": camera_count,
        "top_minerals": top_minerals,
        "latest_recognitions": latest_recognitions,
    })


def gallery(request):
    recognitions = (
        RecognitionHistory.objects
        .select_related("user", "predicted_mineral")
        .order_by("-created_at")[:50]
    )

    return render(request, "pages/gallery.html", {
        "recognitions": recognitions,
    })


def history(request):
    recognitions = (
        RecognitionHistory.objects
        .select_related("user", "predicted_mineral")
        .order_by("-created_at")
    )
    return render(request, "pages/history.html", {
        "recognitions": recognitions
    })


def mineral_autocomplete(request):
    q = request.GET.get("q", "").strip()

    if not q:
        return JsonResponse({"results": []})

    minerals = (
        Mineral.objects
        .filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(formula__icontains=q) |
            Q(color__icontains=q)
        )
        .order_by("title")[:8]
    )

    results = [
        {
            "title": mineral.title,
            "slug": mineral.slug,
            "category": mineral.get_category_display(),
            "formula": mineral.formula or "",
            "url": f"/collection/{mineral.slug}/",
        }
        for mineral in minerals
    ]

    return JsonResponse({"results": results})
