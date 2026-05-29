from django.db import models

from .school_class import SchoolClass
from .school_year import SchoolYear


class Subject(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Kód předmětu")
    name = models.CharField(max_length=120, verbose_name="Název předmětu")
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = ["name"]
        verbose_name = "Předmět"
        verbose_name_plural = "Předměty"

    def __str__(self):
        return f"{self.code} - {self.name}"


class SubjectInSchoolYear(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="school_year_entries",
        verbose_name="Předmět",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="subject_entries",
        verbose_name="Školní rok",
    )
    name = models.CharField(max_length=120, verbose_name="Název v daném školním roce")
    abbreviation = models.CharField(max_length=20, blank=True, verbose_name="Zkratka")
    is_taught = models.BooleanField(default=True, verbose_name="Vyučovaný")

    class Meta:
        ordering = ["-school_year__name", "name"]
        verbose_name = "Předmět ve školním roce"
        verbose_name_plural = "Předměty ve školním roce"
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "school_year"],
                name="unique_subject_per_school_year",
            )
        ]

    def __str__(self):
        return f"{self.school_year} | {self.subject.code}"


class SubjectClassInSchoolYear(models.Model):
    predmet_ve_skolnim_roce = models.ForeignKey(
        SubjectInSchoolYear,
        on_delete=models.PROTECT,
        related_name="tridni_vazby",
        verbose_name="Předmět ve školním roce",
    )
    trida = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name="predmetove_vazby",
        verbose_name="Třída",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = ["-predmet_ve_skolnim_roce__school_year__name", "trida__name", "predmet_ve_skolnim_roce__name"]
        verbose_name = "Předměty tříd ve školním roce"
        verbose_name_plural = "Předměty tříd ve školním roce"
        constraints = [
            models.UniqueConstraint(
                fields=["predmet_ve_skolnim_roce", "trida"],
                name="unique_subject_class_in_school_year",
            )
        ]

    def __str__(self):
        return f"{self.predmet_ve_skolnim_roce} | {self.trida}"
