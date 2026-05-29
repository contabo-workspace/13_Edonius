from django import forms

from core.models import SchoolClass, SchoolYear, StudyFieldInSchoolYear, SubjectInSchoolYear


class GarantTematickyPlanFilterForm(forms.Form):
    school_year = forms.ModelChoiceField(
        queryset=SchoolYear.objects.none(),
        required=False,
        label="Školní rok",
        empty_label="Všechny školní roky",
    )
    study_field = forms.ModelChoiceField(
        queryset=StudyFieldInSchoolYear.objects.none(),
        required=False,
        label="Obor ve školním roce",
        empty_label="Všechny obory",
    )
    subject = forms.ModelChoiceField(
        queryset=SubjectInSchoolYear.objects.none(),
        required=False,
        label="Předmět ve školním roce",
        empty_label="Všechny předměty",
    )
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.none(),
        required=False,
        label="Třída",
        empty_label="Všechny třídy",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["school_year"].queryset = SchoolYear.objects.order_by("-name")

        study_field_queryset = StudyFieldInSchoolYear.objects.filter(is_active=True).select_related(
            "school_year", "obor"
        )
        subject_queryset = SubjectInSchoolYear.objects.filter(is_taught=True).select_related(
            "school_year", "subject"
        )
        school_class_queryset = SchoolClass.objects.filter(is_active=True).select_related("school_year")

        school_year = self.data.get("school_year") or self.initial.get("school_year")
        if school_year:
            study_field_queryset = study_field_queryset.filter(school_year_id=school_year)
            subject_queryset = subject_queryset.filter(school_year_id=school_year)
            school_class_queryset = school_class_queryset.filter(school_year_id=school_year)

        self.fields["study_field"].queryset = study_field_queryset.order_by("-school_year__name", "zkratka", "nazev")
        self.fields["subject"].queryset = subject_queryset.order_by("-school_year__name", "name")
        self.fields["school_class"].queryset = school_class_queryset.order_by("-school_year__name", "name")
