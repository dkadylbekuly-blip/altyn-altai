from django.urls import path
from . import views

app_name = "recognize"

urlpatterns = [
    path("upload/", views.upload_view, name="upload"),
    path("camera/", views.camera_view, name="camera"),
    path("result/<int:pk>/", views.result_view, name="result"),
]
