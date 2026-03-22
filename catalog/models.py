from django.db import models


class Mineral(models.Model):
    CATEGORY_CHOICES = [
        ("mineral", "Минерал"),
        ("rock", "Горная порода"),
        ("glass", "Вулканическое стекло"),
        ("gem", "Драгоценный камень"),
    ]

    slug = models.SlugField(
        max_length=120,
        unique=True,
        verbose_name="Ключ модели",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Название",
    )

    formula = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Формула",
    )

    color = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Цвет",
    )

    hardness = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Твёрдость",
    )

    origin = models.TextField(
        blank=True,
        verbose_name="Происхождение",
    )

    usage = models.TextField(
        blank=True,
        verbose_name="Применение",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    facts = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Интересные факты",
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="mineral",
        verbose_name="Категория",
    )

    image = models.ImageField(
        upload_to="minerals/",
        blank=True,
        null=True,
        verbose_name="Фото",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Минерал"
        verbose_name_plural = "Минералы"
        ordering = ["title"]

    def __str__(self):
        return self.title