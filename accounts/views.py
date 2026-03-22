from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from pages.models import RecognitionHistory


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:cabinet")

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("accounts:cabinet")

    return render(request, "accounts/login.html", {
        "form": form,
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:cabinet")

    form = UserCreationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:cabinet")

    return render(request, "accounts/register.html", {
        "form": form,
    })

def cabinet_view(request):

    recognitions = (
        RecognitionHistory.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(request, "accounts/cabinet.html", {
        "recognitions": recognitions
    })