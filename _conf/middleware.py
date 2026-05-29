import logging
import time

from django.db import connection
from django.conf import settings
from django.shortcuts import redirect, resolve_url


logger = logging.getLogger("edonius.perf")


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            return self.get_response(request)

        login_url = resolve_url(settings.LOGIN_URL)
        path = request.path_info

        if self._is_exempt_path(path, login_url):
            return self.get_response(request)

        return redirect(f"{login_url}?next={request.get_full_path()}")

    def _is_exempt_path(self, path, login_url):
        exempt_prefixes = [
            login_url,
            "/accounts/",
            "/admin/",
            settings.STATIC_URL,
        ]

        media_url = getattr(settings, "MEDIA_URL", None)
        if media_url and media_url != "/":
            exempt_prefixes.append(media_url)

        return any(path.startswith(prefix) for prefix in exempt_prefixes if prefix)


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or ""
        if self._is_exempt_path(path):
            return self.get_response(request)

        start = time.perf_counter()
        initial_query_count = len(connection.queries) if settings.DEBUG else 0
        response = self.get_response(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        query_count = (len(connection.queries) - initial_query_count) if settings.DEBUG else 0

        level = logging.WARNING if elapsed_ms >= 700 or query_count >= 80 else logging.INFO
        logger.log(
            level,
            "%s %s -> %s in %.1fms (%s SQL)",
            request.method,
            request.get_full_path(),
            getattr(response, "status_code", "?"),
            elapsed_ms,
            query_count,
        )
        return response

    def _is_exempt_path(self, path):
        prefixes = [settings.STATIC_URL]

        media_url = getattr(settings, "MEDIA_URL", None)
        if media_url and media_url != "/":
            prefixes.append(media_url)

        return any(path.startswith(prefix) for prefix in prefixes if prefix)
