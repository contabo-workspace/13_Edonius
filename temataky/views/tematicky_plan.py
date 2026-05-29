from django.core.exceptions import PermissionDenied
from django.db.models import Count, IntegerField, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.school_year_context import get_school_year_state
from core.utils import get_user_shortcut

from temataky.forms import GarantTematickyPlanFilterForm, TematickyPlanForm
from temataky.models import TematickeTema, TematickyPlan, TematickyPlanTrida
from temataky.views.permissions import (
    user_can_create_temataky,
    user_can_manage_all_temataky,
    visible_temataky_queryset,
)


def _annotate_temataky_queryset(queryset):
    tema_hours_subquery = (
        TematickeTema.objects.filter(tematicky_plan=OuterRef("pk"))
        .values("tematicky_plan")
        .annotate(total=Sum("hodiny"))
        .values("total")[:1]
    )
    tema_count_subquery = (
        TematickeTema.objects.filter(tematicky_plan=OuterRef("pk"))
        .values("tematicky_plan")
        .annotate(total=Count("id"))
        .values("total")[:1]
    )
    trida_count_subquery = (
        TematickyPlanTrida.objects.filter(tematicky_plan=OuterRef("pk"))
        .values("tematicky_plan")
        .annotate(total=Count("id"))
        .values("total")[:1]
    )

    return (
        queryset.select_related(
            "owner",
            "obor_ve_skolnim_roce",
            "obor_ve_skolnim_roce__school_year",
            "predmet_ve_skolnim_roce",
            "predmet_ve_skolnim_roce__school_year",
        )
        .prefetch_related("tridy__trida", "ucitele__teacher_profile")
        .annotate(
            pocet_hodin=Coalesce(Subquery(tema_hours_subquery, output_field=IntegerField()), 0),
            pocet_temat=Coalesce(Subquery(tema_count_subquery, output_field=IntegerField()), 0),
            pocet_trid=Coalesce(Subquery(trida_count_subquery, output_field=IntegerField()), 0),
            pocet_ucitelu=Count("ucitele", distinct=True),
        )
        .distinct()
    )


def _attach_teacher_shortcuts(plany):
    for plan in plany:
        zkratky = [get_user_shortcut(teacher) for teacher in plan.ucitele.all()]
        plan.ucitele_zkratky = ", ".join(zkratky) if zkratky else "-"

        tridy = [vztah.trida.name for vztah in plan.tridy.all()]
        plan.tridy_display = ", ".join(tridy) if tridy else "-"

    return plany


def temataky_index(request):
    school_year_state = get_school_year_state(request)
    active_school_year = school_year_state["effective_year"]
    can_manage_all = user_can_manage_all_temataky(request.user)
    plany = _attach_teacher_shortcuts(
        _annotate_temataky_queryset(visible_temataky_queryset(request.user, school_year=active_school_year))
    )

    return render(request, "temataky/index.html", {"plany": plany, "can_manage_all": can_manage_all})


def temataky_garant_overview(request):
    if not user_can_manage_all_temataky(request.user):
        raise PermissionDenied("Nemáš oprávnění zobrazit garantský přehled tematických plánů.")

    school_year_state = get_school_year_state(request)
    active_school_year = school_year_state["effective_year"]
    form = GarantTematickyPlanFilterForm(request.GET or None)
    queryset = TematickyPlan.objects.filter(predmet_ve_skolnim_roce__school_year=active_school_year)

    if form.is_valid():
        school_year = form.cleaned_data.get("school_year")
        study_field = form.cleaned_data.get("study_field")
        subject = form.cleaned_data.get("subject")
        school_class = form.cleaned_data.get("school_class")

        if school_year:
            queryset = queryset.filter(predmet_ve_skolnim_roce__school_year=school_year)
        if study_field:
            queryset = queryset.filter(obor_ve_skolnim_roce=study_field)
        if subject:
            queryset = queryset.filter(predmet_ve_skolnim_roce=subject)
        if school_class:
            queryset = queryset.filter(tridy__trida=school_class)

    plany = _attach_teacher_shortcuts(_annotate_temataky_queryset(queryset))

    return render(
        request,
        "temataky/garant_overview.html",
        {
            "filter_form": form,
            "plany": plany,
            "can_manage_all": True,
        },
    )


def temataky_create(request):
    if not user_can_create_temataky(request.user):
        raise PermissionDenied("Nemáš oprávnění vytvářet tematické plány.")

    school_year_state = get_school_year_state(request)
    active_school_year = school_year_state["effective_year"]
    global_school_year = school_year_state["global_year"]
    override_warning = bool(
        active_school_year
        and global_school_year
        and active_school_year.id != global_school_year.id
    )

    if request.method == "POST":
        form = TematickyPlanForm(
            request.POST,
            current_user=request.user,
            can_manage_all=user_can_manage_all_temataky(request.user),
            active_school_year=active_school_year,
        )
        if form.is_valid():
            form.save()
            return redirect("temataky:temataky")
    else:
        form = TematickyPlanForm(
            current_user=request.user,
            can_manage_all=user_can_manage_all_temataky(request.user),
            active_school_year=active_school_year,
        )

    return render(
        request,
        "temataky/create.html",
        {
            "form": form,
            "form_active_school_year": active_school_year,
            "form_school_year_override_warning": override_warning,
        },
    )


def temataky_edit(request, plan_id):
    school_year_state = get_school_year_state(request)
    active_school_year = school_year_state["effective_year"]
    global_school_year = school_year_state["global_year"]
    override_warning = bool(
        active_school_year
        and global_school_year
        and active_school_year.id != global_school_year.id
    )

    plan = get_object_or_404(visible_temataky_queryset(request.user, school_year=active_school_year), pk=plan_id)

    if request.method == "POST":
        form = TematickyPlanForm(
            request.POST,
            instance=plan,
            current_user=request.user,
            can_manage_all=user_can_manage_all_temataky(request.user),
            active_school_year=active_school_year,
        )
        if form.is_valid():
            form.save()
            return redirect("temataky:temataky")
    else:
        form = TematickyPlanForm(
            instance=plan,
            current_user=request.user,
            can_manage_all=user_can_manage_all_temataky(request.user),
            active_school_year=active_school_year,
        )

    return render(
        request,
        "temataky/edit.html",
        {
            "form": form,
            "plan": plan,
            "form_active_school_year": active_school_year,
            "form_school_year_override_warning": override_warning,
        },
    )


@require_POST
def temataky_delete(request, plan_id):
    school_year_state = get_school_year_state(request)
    active_school_year = school_year_state["effective_year"]

    if user_can_manage_all_temataky(request.user):
        plan = get_object_or_404(TematickyPlan, pk=plan_id, predmet_ve_skolnim_roce__school_year=active_school_year)
    else:
        plan = get_object_or_404(
            TematickyPlan,
            pk=plan_id,
            owner=request.user,
            predmet_ve_skolnim_roce__school_year=active_school_year,
        )

    plan.delete()
    return redirect("temataky:temataky")
