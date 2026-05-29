from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


class SchoolYear(models.Model):
    name = models.CharField(
        max_length=7,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{4}/\d{2}$",
                message="Použij formát RRRR/YY, např. 2025/26.",
            )
        ],
    )

    class Meta:
        ordering = ["-name"]
        verbose_name = "Školní rok"
        verbose_name_plural = "Školní roky"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if "/" not in self.name:
            return

        start, end = self.name.split("/", maxsplit=1)
        if len(start) != 4 or len(end) != 2 or not start.isdigit() or not end.isdigit():
            return

        expected_end = f"{(int(start) + 1) % 100:02d}"
        if end != expected_end:
            raise ValidationError({"name": "Druhý rok musí navazovat, např. 2025/26."})
