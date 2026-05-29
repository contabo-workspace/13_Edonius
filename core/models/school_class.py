from django.db import models

from .school_year import SchoolYear


class SchoolClass(models.Model):
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="classes",
        verbose_name="Školní rok",
    )
    name = models.CharField(max_length=20, verbose_name="Název třídy")
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = ["-school_year__name", "name"]
        verbose_name = "Třída"
        verbose_name_plural = "Třídy"
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "name"],
                name="unique_class_name_per_school_year",
            )
        ]

    def __str__(self):
        return f"{self.school_year} | {self.name}"
