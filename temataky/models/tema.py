from django.db import models
from django.db.models import Sum


class TematickeTema(models.Model):
    tematicky_plan = models.ForeignKey(
        "temataky.TematickyPlan",
        on_delete=models.CASCADE,
        related_name="temata",
        verbose_name="Tematický plán",
    )
    poradi = models.PositiveSmallIntegerField(verbose_name="Pořadí")
    nazev = models.CharField(max_length=150, verbose_name="Název tématu")
    hodiny = models.PositiveSmallIntegerField(verbose_name="Počet hodin")

    class Meta:
        ordering = ["poradi", "id"]
        verbose_name = "Téma tematického plánu"
        verbose_name_plural = "Témata tematického plánu"
        constraints = [
            models.UniqueConstraint(
                fields=["tematicky_plan", "poradi"],
                name="unique_tema_poradi_per_plan",
            )
        ]

    def __str__(self):
        return f"{self.tematicky_plan.nazev} | {self.poradi}. {self.nazev}"

    @property
    def soucet_hodin_bodu(self):
        return self.body.aggregate(total=Sum("hodiny")).get("total") or 0


class TemaBod(models.Model):
    tema = models.ForeignKey(
        TematickeTema,
        on_delete=models.CASCADE,
        related_name="body",
        verbose_name="Téma",
    )
    poradi = models.PositiveSmallIntegerField(verbose_name="Pořadí")
    nazev = models.CharField(max_length=200, verbose_name="Název bodu")
    hodiny = models.PositiveSmallIntegerField(verbose_name="Počet hodin")

    class Meta:
        ordering = ["poradi", "id"]
        verbose_name = "Bod tématu"
        verbose_name_plural = "Body tématu"
        constraints = [
            models.UniqueConstraint(
                fields=["tema", "poradi"],
                name="unique_bod_poradi_per_tema",
            )
        ]

    def __str__(self):
        return f"{self.tema} | {self.poradi}. {self.nazev}"
