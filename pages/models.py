from django.conf import settings
from django.db import models


class RecognitionHistory(models.Model):
    SOURCE_CHOICES = [
        ("upload", "Загрузка"),
        ("camera", "Камера"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recognitions",
        verbose_name="Пользователь",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата распознавания")
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="upload", verbose_name="Источник")

    image = models.ImageField(upload_to="recognitions/", blank=True, null=True, verbose_name="Фото")

    predicted_mineral = models.ForeignKey(
        "catalog.Mineral",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recognitions",
        verbose_name="Распознанный минерал",
    )

    top1_label = models.CharField(max_length=120, blank=True, default="", verbose_name="Top-1 минерал")
    top1_conf = models.FloatField(blank=True, null=True, verbose_name="Top-1 вероятность")

    top2_label = models.CharField(max_length=120, blank=True, default="", verbose_name="Top-2 минерал")
    top2_conf = models.FloatField(blank=True, null=True, verbose_name="Top-2 вероятность")

    top3_label = models.CharField(max_length=120, blank=True, default="", verbose_name="Top-3 минерал")
    top3_conf = models.FloatField(blank=True, null=True, verbose_name="Top-3 вероятность")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "История распознавания"
        verbose_name_plural = "История распознаваний"

    def __str__(self):
        return f"{self.user} • {self.top1_label or '—'} • {self.created_at:%Y-%m-%d %H:%M}"