from django.urls import path

from .views import temataky_create, temataky_delete, temataky_edit, temataky_garant_overview, temataky_index

app_name = "temataky"

urlpatterns = [
    path("", temataky_index, name="temataky"),
    path("garant/", temataky_garant_overview, name="temataky-garant-overview"),
    path("create/", temataky_create, name="temataky-create"),
    path("<int:plan_id>/edit/", temataky_edit, name="temataky-edit"),
    path("<int:plan_id>/delete/", temataky_delete, name="temataky-delete"),
]
