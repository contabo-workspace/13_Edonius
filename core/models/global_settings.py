from django.db import models


class GlobalSettings(models.Model):
    active_school_year = models.ForeignKey(
        "core.SchoolYear",
        on_delete=models.PROTECT,
        related_name="global_settings_entries",
        verbose_name="Aktivní školní rok",
    )

    class Meta:
        verbose_name = "Globální nastavení"
        verbose_name_plural = "Globální nastavení"

    def __str__(self):
        return f"Aktivní rok: {self.active_school_year}"
