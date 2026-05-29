from django.contrib import admin

from .models import (
	SchoolYear,
	SchoolClass,
	StudyField,
	StudyFieldInSchoolYear,
	Subject,
	SubjectInSchoolYear,
	SubjectClassInSchoolYear,
	Teacher,
	TeachingGroupInSchoolYear,
	TeacherAssignment,
	UserProfile,
	GlobalSettings,
)


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)
	ordering = ("-name",)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
	list_display = ("school_year", "name", "is_active")
	list_filter = ("school_year",)
	search_fields = ("name", "school_year__name")
	autocomplete_fields = ("school_year",)
	ordering = ("-school_year__name", "name")


@admin.register(StudyField)
class StudyFieldAdmin(admin.ModelAdmin):
	list_display = ("cislo_oboru", "zkratka", "nazev", "is_active")
	search_fields = ("cislo_oboru", "zkratka", "nazev")
	ordering = ("nazev",)


@admin.register(StudyFieldInSchoolYear)
class StudyFieldInSchoolYearAdmin(admin.ModelAdmin):
	list_display = ("school_year", "obor", "zkratka", "nazev", "is_active")
	list_filter = ("school_year",)
	search_fields = ("zkratka", "nazev", "obor__cislo_oboru", "obor__nazev")
	autocomplete_fields = ("obor", "school_year")
	ordering = ("-school_year__name", "nazev")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
	list_display = ("code", "name", "is_active")
	list_filter = ("school_year_entries__school_year",)
	search_fields = ("code", "name")
	ordering = ("name",)


@admin.register(SubjectInSchoolYear)
class SubjectInSchoolYearAdmin(admin.ModelAdmin):
	list_display = ("school_year", "subject", "name", "abbreviation", "is_taught")
	list_filter = ("school_year",)
	search_fields = ("name", "abbreviation", "subject__code", "subject__name")
	autocomplete_fields = ("subject", "school_year")
	ordering = ("-school_year__name", "name")


@admin.register(SubjectClassInSchoolYear)
class SubjectClassInSchoolYearAdmin(admin.ModelAdmin):
	list_display = ("predmet_ve_skolnim_roce", "trida", "is_active")
	list_filter = ("predmet_ve_skolnim_roce__school_year",)
	search_fields = (
		"predmet_ve_skolnim_roce__name",
		"predmet_ve_skolnim_roce__subject__name",
		"predmet_ve_skolnim_roce__subject__code",
		"trida__name",
	)
	autocomplete_fields = ("predmet_ve_skolnim_roce", "trida")
	ordering = ("-predmet_ve_skolnim_roce__school_year__name", "trida__name", "predmet_ve_skolnim_roce__name")


@admin.register(TeachingGroupInSchoolYear)
class TeachingGroupInSchoolYearAdmin(admin.ModelAdmin):
	list_display = ("school_year", "code", "name", "is_active")
	list_filter = ("school_year",)
	search_fields = ("code", "name", "school_year__name")
	autocomplete_fields = ("school_year",)
	ordering = ("-school_year__name", "name")


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
	list_display = ("teacher", "subject_class_in_school_year", "group_in_school_year", "is_active")
	list_filter = ("subject_class_in_school_year__predmet_ve_skolnim_roce__school_year",)
	search_fields = (
		"teacher__username",
		"teacher__first_name",
		"teacher__last_name",
		"subject_class_in_school_year__predmet_ve_skolnim_roce__subject__name",
		"subject_class_in_school_year__trida__name",
		"group_in_school_year__name",
	)
	autocomplete_fields = ("teacher", "subject_class_in_school_year", "group_in_school_year")
	ordering = ("-subject_class_in_school_year__predmet_ve_skolnim_roce__school_year__name", "teacher__last_name")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
	list_display = ("shortcut", "user", "is_active")
	list_filter = ("is_active",)
	search_fields = ("shortcut", "user__username", "user__first_name", "user__last_name")
	autocomplete_fields = ("user",)
	ordering = ("shortcut",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "photo")
	search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
	autocomplete_fields = ("user",)
	ordering = ("user__username",)


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
	list_display = ("active_school_year",)
	autocomplete_fields = ("active_school_year",)

	def has_add_permission(self, request):
		if GlobalSettings.objects.exists():
			return False
		return super().has_add_permission(request)
