from django.contrib import admin
from .models import RecognitionHistory


@admin.register(RecognitionHistory)
class RecognitionHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "top1_label", "top1_conf", "source", "created_at")
    list_filter = ("source", "created_at")
    search_fields = ("user__username", "top1_label", "top2_label", "top3_label")