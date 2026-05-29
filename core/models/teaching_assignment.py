from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .school_year import SchoolYear
from .subject import SubjectClassInSchoolYear


class TeachingGroupInSchoolYear(models.Model):
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="teaching_groups",
        verbose_name="Školní rok",
    )
    name = models.CharField(max_length=50, verbose_name="Název skupiny")
    code = models.CharField(max_length=30, blank=True, verbose_name="Kód skupiny")
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = ["-school_year__name", "name"]
        verbose_name = "Skupina ve školním roce"
        verbose_name_plural = "Skupiny ve školním roce"
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "name"],
                name="unique_teaching_group_name_per_school_year",
            ),
        ]

    def __str__(self):
        if self.code:
            return f"{self.school_year} | {self.code} | {self.name}"
        return f"{self.school_year} | {self.name}"


class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="teaching_assignments",
        verbose_name="Učitel",
    )
    subject_class_in_school_year = models.ForeignKey(
        SubjectClassInSchoolYear,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
        verbose_name="Předmět a třída ve školním roce",
    )
    group_in_school_year = models.ForeignKey(
        TeachingGroupInSchoolYear,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="teacher_assignments",
        verbose_name="Skupina ve školním roce",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktivní")

    class Meta:
        ordering = [
            "-subject_class_in_school_year__predmet_ve_skolnim_roce__school_year__name",
            "teacher__last_name",
            "teacher__first_name",
        ]
        verbose_name = "Úvazek učitele"
        verbose_name_plural = "Úvazky učitelů"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "subject_class_in_school_year", "group_in_school_year"],
                name="unique_teacher_assignment_per_scope",
            )
        ]

    def clean(self):
        super().clean()
        if not self.group_in_school_year_id or not self.subject_class_in_school_year_id:
            return

        assignment_school_year_id = self.subject_class_in_school_year.predmet_ve_skolnim_roce.school_year_id
        group_school_year_id = self.group_in_school_year.school_year_id

        if assignment_school_year_id != group_school_year_id:
            raise ValidationError(
                {
                    "group_in_school_year": "Skupina musí patřit do stejného školního roku jako úvazek učitele."
                }
            )

    def __str__(self):
        group_part = f" | {self.group_in_school_year.name}" if self.group_in_school_year else ""
        return f"{self.teacher} | {self.subject_class_in_school_year}{group_part}"
