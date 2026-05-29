from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet

from .models import TematickeTema, TematickyPlan, TematickyPlanTrida, TemaBod


class TematickyPlanTridaInline(admin.TabularInline):
	model = TematickyPlanTrida
	extra = 1
	autocomplete_fields = ("trida",)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "trida":
			object_id = request.resolver_match.kwargs.get("object_id") if request.resolver_match else None
			if object_id:
				plan = (
					TematickyPlan.objects.select_related("predmet_ve_skolnim_roce__school_year")
					.filter(pk=object_id)
					.first()
				)
				if plan:
					trida_model = self.model._meta.get_field("trida").remote_field.model
					kwargs["queryset"] = trida_model.objects.filter(
						school_year_id=plan.predmet_ve_skolnim_roce.school_year_id
					)

		return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TematickeTemaInline(admin.TabularInline):
	model = TematickeTema
	extra = 1
	fields = ("poradi", "nazev", "hodiny")


@admin.register(TematickyPlan)
class TematickyPlanAdmin(admin.ModelAdmin):
	inlines = (TematickyPlanTridaInline, TematickeTemaInline)
	list_display = (
		"nazev",
		"owner",
		"obor_ve_skolnim_roce",
		"predmet_ve_skolnim_roce",
		"pocet_temat",
		"pocet_trid",
		"pocet_ucitelu",
		"is_aktivni",
		"created_at",
		"updated_at",
	)
	list_filter = (
		"predmet_ve_skolnim_roce__school_year",
		"obor_ve_skolnim_roce",
	)
	search_fields = (
		"nazev",
		"obor_ve_skolnim_roce__nazev",
		"obor_ve_skolnim_roce__zkratka",
		"obor_ve_skolnim_roce__obor__cislo_oboru",
		"predmet_ve_skolnim_roce__name",
		"predmet_ve_skolnim_roce__subject__name",
		"predmet_ve_skolnim_roce__subject__code",
		"owner__first_name",
		"owner__last_name",
		"owner__username",
		"ucitele__first_name",
		"ucitele__last_name",
		"ucitele__username",
	)
	autocomplete_fields = ("owner", "obor_ve_skolnim_roce", "predmet_ve_skolnim_roce", "ucitele")
	ordering = ("-created_at",)

	def pocet_trid(self, obj):
		return obj.tridy.count()

	pocet_trid.short_description = "Počet tříd"

	def pocet_temat(self, obj):
		return obj.temata.count()

	pocet_temat.short_description = "Počet témat"

	def pocet_ucitelu(self, obj):
		return obj.ucitele.count()

	pocet_ucitelu.short_description = "Počet učitelů"


@admin.register(TematickyPlanTrida)
class TematickyPlanTridaAdmin(admin.ModelAdmin):
	list_display = ("tematicky_plan", "trida")
	list_filter = ("trida__school_year",)
	search_fields = ("tematicky_plan__nazev", "trida__name")
	autocomplete_fields = ("tematicky_plan", "trida")


class TemaBodInlineFormSet(BaseInlineFormSet):
	def clean(self):
		super().clean()
		total = 0
		for form in self.forms:
			if not hasattr(form, "cleaned_data"):
				continue
			if not form.cleaned_data or form.cleaned_data.get("DELETE"):
				continue
			total += form.cleaned_data.get("hodiny") or 0

		tema = self.instance
		if tema and tema.pk and total != tema.hodiny:
			raise ValidationError(
				f"Součet hodin bodů ({total}) musí odpovídat hodinám tématu ({tema.hodiny})."
			)


class TemaBodInline(admin.TabularInline):
	model = TemaBod
	extra = 1
	fields = ("poradi", "nazev", "hodiny")
	formset = TemaBodInlineFormSet


@admin.register(TematickeTema)
class TematickeTemaAdmin(admin.ModelAdmin):
	inlines = (TemaBodInline,)
	list_display = ("tematicky_plan", "poradi", "nazev", "hodiny", "soucet_hodin_bodu")
	list_filter = ("tematicky_plan__predmet_ve_skolnim_roce__school_year",)
	search_fields = (
		"nazev",
		"tematicky_plan__nazev",
		"tematicky_plan__predmet_ve_skolnim_roce__subject__name",
	)
	autocomplete_fields = ("tematicky_plan",)
	ordering = ("tematicky_plan", "poradi")


@admin.register(TemaBod)
class TemaBodAdmin(admin.ModelAdmin):
	list_display = ("tema", "poradi", "nazev", "hodiny")
	list_filter = ("tema__tematicky_plan__predmet_ve_skolnim_roce__school_year",)
	search_fields = ("nazev", "tema__nazev", "tema__tematicky_plan__nazev")
	autocomplete_fields = ("tema",)
	ordering = ("tema", "poradi")
