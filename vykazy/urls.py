from django.urls import path

from .views import vykazy_index

app_name = "vykazy"

urlpatterns = [
    path("", vykazy_index, name="vykazy"),
]
