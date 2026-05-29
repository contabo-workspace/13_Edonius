from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from core.school_year_context import set_school_year_override


@require_POST
def school_year_switch_view(request):
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "dashboard:dashboard"
    school_year_id = request.POST.get("school_year_id")

    try:
        set_school_year_override(request, school_year_id)
    except ValidationError as exc:
        messages.error(request, str(exc))
    else:
        if school_year_id:
            messages.info(request, "Pracovní školní rok byl změněn.")
        else:
            messages.info(request, "Byl nastaven aktuální školní rok.")

    return redirect(next_url)
