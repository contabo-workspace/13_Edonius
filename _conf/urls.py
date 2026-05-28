from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('maturity/', include('imp.urls')),
    path('temataky/', include('temataky.urls')),
    path('vykazy/', include('vykazy.urls')),
]
