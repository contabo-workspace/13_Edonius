from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class TematickyPlan(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_tematicke_plany",
        verbose_name="Vlastník",
    )
    obor_ve_skolnim_roce = models.ForeignKey(
        "core.StudyFieldInSchoolYear",
        on_delete=models.PROTECT,
        related_name="tematicke_plany",
        null=True,
        verbose_name="Obor ve školním roce",
    )
    predmet_ve_skolnim_roce = models.ForeignKey(
        "core.SubjectInSchoolYear",
        on_delete=models.PROTECT,
        related_name="tematicke_plany",
        verbose_name="Předmět ve školním roce",
    )
    ucitele = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="tematicke_plany",
        verbose_name="Učitelé",
    )
    nazev = models.CharField(max_length=150, verbose_name="Název tematického plánu")
    popis = models.TextField(blank=True, verbose_name="Popis")
    is_aktivni = models.BooleanField(default=True, verbose_name="Aktivní")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvořeno")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Upraveno")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Tematický plán"
        verbose_name_plural = "Tematické plány"
        constraints = [
            models.UniqueConstraint(
                fields=["obor_ve_skolnim_roce", "predmet_ve_skolnim_roce", "nazev"],
                name="unique_plan_name_per_field_subject_in_school_year",
            )
        ]

    def clean(self):
        super().clean()

        if not self.obor_ve_skolnim_roce_id or not self.predmet_ve_skolnim_roce_id:
            return

        if self.obor_ve_skolnim_roce.school_year_id != self.predmet_ve_skolnim_roce.school_year_id:
            raise ValidationError(
                {
                    "obor_ve_skolnim_roce": "Obor musí patřit do stejného školního roku jako předmět tematického plánu."
                }
            )

    def __str__(self):
        return f"{self.obor_ve_skolnim_roce} | {self.predmet_ve_skolnim_roce} | {self.nazev}"


class TematickyPlanTrida(models.Model):
    tematicky_plan = models.ForeignKey(
        TematickyPlan,
        on_delete=models.CASCADE,
        related_name="tridy",
        verbose_name="Tematický plán",
    )
    trida = models.ForeignKey(
        "core.SchoolClass",
        on_delete=models.PROTECT,
        related_name="tematicke_plany",
        verbose_name="Třída",
    )

    class Meta:
        ordering = ["trida__name"]
        verbose_name = "Třída tematického plánu"
        verbose_name_plural = "Třídy tematického plánu"
        constraints = [
            models.UniqueConstraint(
                fields=["tematicky_plan", "trida"],
                name="unique_class_per_thematic_plan",
            )
        ]

    def __str__(self):
        return f"{self.tematicky_plan.nazev} | {self.trida}"

    def clean(self):
        super().clean()

        if not self.tematicky_plan_id or not self.trida_id:
            return

        plan_school_year_id = self.tematicky_plan.predmet_ve_skolnim_roce.school_year_id
        class_school_year_id = self.trida.school_year_id

        if plan_school_year_id != class_school_year_id:
            raise ValidationError(
                {
                    "trida": "Třída musí patřit do stejného školního roku jako předmět tematického plánu."
                }
            )
