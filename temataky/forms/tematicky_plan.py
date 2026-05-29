from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

from core.models import SchoolClass
from core.utils import get_user_display_with_shortcut

from temataky.models import TematickyPlan, TematickyPlanTrida


class TeacherModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return get_user_display_with_shortcut(obj)


class TematickyPlanForm(forms.ModelForm):
    ucitele = TeacherModelMultipleChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Učitelé",
    )
    tridy = forms.ModelMultipleChoiceField(
        queryset=SchoolClass.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label="Třídy",
    )

    class Meta:
        model = TematickyPlan
        fields = [
            "nazev",
            "obor_ve_skolnim_roce",
            "predmet_ve_skolnim_roce",
            "owner",
            "ucitele",
            "tridy",
            "is_aktivni",
            "popis",
        ]

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        self.can_manage_all = kwargs.pop("can_manage_all", False)
        self.active_school_year = kwargs.pop("active_school_year", None)
        super().__init__(*args, **kwargs)
        user_model = get_user_model()
        active_users = user_model.objects.filter(is_active=True).order_by("last_name", "first_name", "username")

        if self.can_manage_all:
            self.fields["owner"].queryset = active_users
            self.fields["owner"].label_from_instance = get_user_display_with_shortcut
        else:
            self.fields.pop("owner")

        self.fields["ucitele"].queryset = user_model.objects.filter(is_active=True).order_by(
            "last_name", "first_name", "username"
        )
        self.fields["obor_ve_skolnim_roce"].queryset = self.fields["obor_ve_skolnim_roce"].queryset.filter(
            is_active=True
        ).select_related("school_year", "obor")
        self.fields["predmet_ve_skolnim_roce"].queryset = self.fields["predmet_ve_skolnim_roce"].queryset.filter(
            is_taught=True
        ).select_related("school_year", "subject")

        if self.active_school_year:
            self.fields["obor_ve_skolnim_roce"].queryset = self.fields["obor_ve_skolnim_roce"].queryset.filter(
                school_year=self.active_school_year
            )
            self.fields["predmet_ve_skolnim_roce"].queryset = self.fields["predmet_ve_skolnim_roce"].queryset.filter(
                school_year=self.active_school_year
            )

        predmet_id = self.data.get("predmet_ve_skolnim_roce") or (
            self.instance.predmet_ve_skolnim_roce_id if self.instance and self.instance.pk else None
        )
        tridy_qs = SchoolClass.objects.filter(is_active=True).select_related("school_year")
        if self.active_school_year:
            tridy_qs = tridy_qs.filter(school_year=self.active_school_year)
        if predmet_id:
            try:
                selected_subject = self.fields["predmet_ve_skolnim_roce"].queryset.get(pk=predmet_id)
                tridy_qs = tridy_qs.filter(school_year_id=selected_subject.school_year_id)
            except (ValueError, TypeError, self.fields["predmet_ve_skolnim_roce"].queryset.model.DoesNotExist):
                pass
        self.fields["tridy"].queryset = tridy_qs.order_by("school_year__name", "name")

        if self.instance and self.instance.pk:
            self.initial["tridy"] = self.instance.tridy.values_list("trida_id", flat=True)
        elif self.current_user:
            self.initial["ucitele"] = [self.current_user.pk]

        if self.can_manage_all and "owner" in self.fields and self.current_user and not self.instance.pk:
            self.initial["owner"] = self.current_user.pk

    def clean(self):
        cleaned_data = super().clean()
        predmet = cleaned_data.get("predmet_ve_skolnim_roce")
        tridy = cleaned_data.get("tridy")
        ucitele = cleaned_data.get("ucitele")

        owner = cleaned_data.get("owner") if self.can_manage_all and "owner" in self.fields else None
        if not owner:
            owner = self.instance.owner if self.instance and self.instance.pk else self.current_user

        if not owner:
            raise forms.ValidationError("Nepodařilo se určit vlastníka tematického plánu.")

        if ucitele is not None and owner not in ucitele:
            self.add_error("ucitele", "Vlastník tematického plánu musí být mezi učiteli.")

        if (
            ucitele is not None
            and self.instance
            and self.instance.pk
            and self.current_user
            and self.instance.owner_id == self.current_user.id
            and self.current_user not in ucitele
        ):
            self.add_error("ucitele", "Vlastník sebe nemůže odebrat ze seznamu učitelů.")

        if not predmet or not tridy:
            return cleaned_data

        invalid_tridy = [trida.name for trida in tridy if trida.school_year_id != predmet.school_year_id]
        if invalid_tridy:
            self.add_error(
                "tridy",
                "Vybrané třídy musí patřit do stejného školního roku jako vybraný předmět. "
                f"Neplatné třídy: {', '.join(invalid_tridy)}",
            )
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        tridy = self.cleaned_data.get("tridy", [])
        plan = super().save(commit=False)

        if self.can_manage_all and "owner" in self.fields:
            plan.owner = self.cleaned_data["owner"]
        elif not plan.owner_id and self.current_user:
            plan.owner = self.current_user

        if not plan.owner_id:
            raise ValueError("Tematický plán musí mít vlastníka.")

        if not commit:
            return plan

        plan.save()
        self.save_m2m()

        if not plan.ucitele.filter(pk=plan.owner_id).exists():
            plan.ucitele.add(plan.owner)

        selected_ids = set(trida.id for trida in tridy)
        existing_ids = set(plan.tridy.values_list("trida_id", flat=True))

        to_remove = existing_ids - selected_ids
        if to_remove:
            TematickyPlanTrida.objects.filter(tematicky_plan=plan, trida_id__in=to_remove).delete()

        to_add = selected_ids - existing_ids
        for trida_id in to_add:
            vztah = TematickyPlanTrida(tematicky_plan=plan, trida_id=trida_id)
            vztah.full_clean()
            vztah.save()

        return plan
