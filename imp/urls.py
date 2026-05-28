from django.urls import path

from .views import maturity, practical_maturity, schedules

app_name = "imp"

urlpatterns = [
    path("", maturity, name="maturity"),
    path("prakticke/", practical_maturity, name="prakticke"),
    path("rozpisy/", schedules, name="rozpisy"),
]
