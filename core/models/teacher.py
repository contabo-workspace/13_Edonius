from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        verbose_name="Uživatel",
    )
    shortcut = models.CharField(
        max_length=8,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z0-9]{1,8}$",
                message="Zkratka může obsahovat jen písmena/čísla (1-8 znaků).",
            )
        ],
        verbose_name="Zkratka učitele",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = ["shortcut"]
        verbose_name = "Učitel"
        verbose_name_plural = "Učitelé"

    def __str__(self):
        full_name = f"{self.user.last_name} {self.user.first_name}".strip()
        return f"{full_name or self.user.username} ({self.shortcut})"
