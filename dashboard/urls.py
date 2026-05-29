from django.urls import path

from .views import dashboard, settings_password_view, settings_photo_view, settings_view

app_name = "dashboard"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("settings/", settings_view, name="settings"),
    path("settings/photo/", settings_photo_view, name="settings-photo"),
    path("settings/password/", settings_password_view, name="settings-password"),
]
