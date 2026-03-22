from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from pages.models import RecognitionHistory
from catalog.models import Mineral
from .ml import predict_image


MINERAL_INFO = {
    "malachite": {
        "title": "Малахит",
        "formula": "Cu₂CO₃(OH)₂",
        "color": "Зелёный",
        "hardness": "3.5–4",
        "origin": "Медные месторождения",
        "usage": "Ювелирные изделия и декоративные камни",
        "description": "Малахит — ярко-зелёный медный минерал с характерным полосчатым рисунком.",
    },
    "quartz": {
        "title": "Кварц",
        "formula": "SiO₂",
        "color": "Бесцветный, белый, розовый",
        "hardness": "7",
        "origin": "Магматические и метаморфические породы",
        "usage": "Стекольная промышленность, электроника",
        "description": "Кварц — один из самых распространённых минералов земной коры.",
    },
    "obsidian": {
        "title": "Обсидиан",
        "formula": "Вулканическое стекло",
        "color": "Чёрный",
        "hardness": "5",
        "origin": "Вулканические извержения",
        "usage": "Декоративные изделия",
        "description": "Обсидиан — природное вулканическое стекло.",
    },
    "fluorite": {
        "title": "Флюорит",
        "formula": "CaF₂",
        "color": "Фиолетовый, зелёный",
        "hardness": "4",
        "origin": "Гидротермальные жилы",
        "usage": "Металлургия, химическая промышленность",
        "description": "Флюорит — красивый минерал с яркой окраской.",
    },
    "azurite": {
        "title": "Азурит",
        "formula": "Cu₃(CO₃)₂(OH)₂",
        "color": "Синий",
        "hardness": "3.5–4",
        "origin": "Медные месторождения",
        "usage": "Коллекционные образцы",
        "description": "Азурит — медный минерал ярко-синего цвета.",
    },
    "granite": {
        "title": "Гранит",
        "formula": "Горная порода",
        "color": "Серый, розовый",
        "hardness": "Высокая",
        "origin": "Магматическая порода",
        "usage": "Строительство",
        "description": "Гранит — прочная магматическая горная порода.",
    },
}


def normalize_label(label: str) -> str:
    return (label or "").strip().lower().replace(" ", "").replace("-", "")


def find_predicted_mineral(top1_label: str):
    normalized = normalize_label(top1_label)

    minerals = Mineral.objects.all()
    for mineral in minerals:
        if normalize_label(mineral.title) == normalized:
            return mineral
        if hasattr(mineral, "slug") and normalize_label(mineral.slug) == normalized:
            return mineral

    return None


def get_mineral_info(top1_label: str):
    normalized = normalize_label(top1_label)
    return MINERAL_INFO.get(normalized)


def parse_prediction_item(item):
    if isinstance(item, dict):
        return item.get("label", ""), item.get("confidence", 0)

    if isinstance(item, (list, tuple)):
        label = item[0] if len(item) > 0 else ""
        confidence = item[1] if len(item) > 1 else 0
        return label, confidence

    return "", 0


def extract_top3(preds):
    top1_label, top1_conf = ("", 0)
    top2_label, top2_conf = ("", 0)
    top3_label, top3_conf = ("", 0)

    if len(preds) > 0:
        top1_label, top1_conf = parse_prediction_item(preds[0])

    if len(preds) > 1:
        top2_label, top2_conf = parse_prediction_item(preds[1])

    if len(preds) > 2:
        top3_label, top3_conf = parse_prediction_item(preds[2])

    return (
        top1_label, top1_conf,
        top2_label, top2_conf,
        top3_label, top3_conf,
    )


@login_required
def upload_view(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        if not image_file:
            return render(request, "recognize/upload.html", {
                "error": "Пожалуйста, выберите изображение."
            })

        preds = predict_image(image_file)

        (
            top1_label, top1_conf,
            top2_label, top2_conf,
            top3_label, top3_conf,
        ) = extract_top3(preds)

        predicted_mineral = find_predicted_mineral(top1_label)

        item = RecognitionHistory.objects.create(
            user=request.user,
            source="upload",
            image=image_file,
            top1_label=top1_label,
            top1_conf=top1_conf,
            top2_label=top2_label,
            top2_conf=top2_conf,
            top3_label=top3_label,
            top3_conf=top3_conf,
            predicted_mineral=predicted_mineral,
        )

        return redirect("recognize:result", pk=item.pk)

    return render(request, "recognize/upload.html")


@login_required
def camera_view(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        if not image_file:
            return render(request, "recognize/camera.html", {
                "error": "Снимок не был получен."
            })

        preds = predict_image(image_file)

        (
            top1_label, top1_conf,
            top2_label, top2_conf,
            top3_label, top3_conf,
        ) = extract_top3(preds)

        predicted_mineral = find_predicted_mineral(top1_label)

        item = RecognitionHistory.objects.create(
            user=request.user,
            source="camera",
            image=image_file,
            top1_label=top1_label,
            top1_conf=top1_conf,
            top2_label=top2_label,
            top2_conf=top2_conf,
            top3_label=top3_label,
            top3_conf=top3_conf,
            predicted_mineral=predicted_mineral,
        )

        return redirect("recognize:result", pk=item.pk)

    return render(request, "recognize/camera.html")


@login_required
def result_view(request, pk):
    item = get_object_or_404(RecognitionHistory, pk=pk, user=request.user)

    mineral_info = get_mineral_info(item.top1_label)
    predicted_mineral = item.predicted_mineral

    similar_candidates = []
    if item.top2_label:
        similar_candidates.append({
            "label": item.top2_label,
            "confidence": item.top2_conf,
        })
    if item.top3_label:
        similar_candidates.append({
            "label": item.top3_label,
            "confidence": item.top3_conf,
        })

    return render(request, "recognize/result.html", {
        "item": item,
        "mineral_info": mineral_info,
        "predicted_mineral": predicted_mineral,
        "similar_candidates": similar_candidates,
    })
