from django.urls import path

from .views import temataky_index

app_name = "temataky"

urlpatterns = [
    path("", temataky_index, name="temataky"),
]
