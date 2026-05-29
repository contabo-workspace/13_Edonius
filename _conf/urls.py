from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf.urls.static import static

from core.views import school_year_switch_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('school-year/switch/', school_year_switch_view, name='school-year-switch'),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('dashboard.urls')),
    path('maturity/', include('imp.urls')),
    path('temataky/', include('temataky.urls')),
    path('vykazy/', include('vykazy.urls')),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = '_conf.error_handlers.bad_request_view'
handler403 = '_conf.error_handlers.permission_denied_view'
handler404 = '_conf.error_handlers.page_not_found_view'
handler500 = '_conf.error_handlers.server_error_view'
