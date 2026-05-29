from django.db import models

from .school_year import SchoolYear


class StudyField(models.Model):
    cislo_oboru = models.CharField(max_length=30, unique=True, verbose_name="Číslo oboru")
    zkratka = models.CharField(max_length=20, unique=True, verbose_name="Zkratka")
    nazev = models.CharField(max_length=150, verbose_name="Název oboru vzdělávání")
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = ["nazev"]
        verbose_name = "Obor vzdělávání"
        verbose_name_plural = "Obory vzdělávání"

    def __str__(self):
        return f"{self.cislo_oboru} | {self.zkratka} | {self.nazev}"


class StudyFieldInSchoolYear(models.Model):
    obor = models.ForeignKey(
        StudyField,
        on_delete=models.PROTECT,
        related_name="school_year_entries",
        verbose_name="Obor vzdělávání",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="study_field_entries",
        verbose_name="Školní rok",
    )
    nazev = models.CharField(max_length=150, verbose_name="Název v daném školním roce")
    zkratka = models.CharField(max_length=20, verbose_name="Zkratka v daném školním roce")
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = ["-school_year__name", "nazev"]
        verbose_name = "Obor vzdělávání ve školním roce"
        verbose_name_plural = "Obory vzdělávání ve školním roce"
        constraints = [
            models.UniqueConstraint(
                fields=["obor", "school_year"],
                name="unique_study_field_per_school_year",
            ),
            models.UniqueConstraint(
                fields=["school_year", "zkratka"],
                name="unique_study_field_abbreviation_per_school_year",
            ),
        ]

    def __str__(self):
        return f"{self.school_year} | {self.zkratka} | {self.nazev}"
