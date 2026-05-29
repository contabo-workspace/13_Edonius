from django.core.exceptions import ValidationError

from core.models import GlobalSettings, SchoolYear


SESSION_OVERRIDE_KEY = "school_year_override_id"
REQUEST_STATE_CACHE_KEY = "_school_year_state_cache"
GROUP_NAMES_CACHE_KEY = "_edonius_group_name_set"


def _user_has_any_group(user, group_names):
    if not getattr(user, "is_authenticated", False):
        return False

    cached_names = getattr(user, GROUP_NAMES_CACHE_KEY, None)
    if cached_names is None:
        cached_names = set(user.groups.values_list("name", flat=True))
        setattr(user, GROUP_NAMES_CACHE_KEY, cached_names)

    return bool(cached_names.intersection(group_names))


def _compute_school_year_state(request):
    user = getattr(request, "user", None) if request else None
    can_override = bool(user and user_can_override_school_year(user))

    settings_obj = GlobalSettings.objects.select_related("active_school_year").first()
    if settings_obj and settings_obj.active_school_year_id:
        global_year = settings_obj.active_school_year
    else:
        global_year = SchoolYear.objects.order_by("-name").first()

    effective_year = global_year
    override_id = None
    if request and can_override:
        override_id = request.session.get(SESSION_OVERRIDE_KEY)
        if override_id:
            effective_year = SchoolYear.objects.filter(pk=override_id).first()
            if not effective_year:
                request.session.pop(SESSION_OVERRIDE_KEY, None)
                effective_year = global_year

    override_active = bool(
        can_override
        and override_id
        and global_year
        and effective_year
        and effective_year.id != global_year.id
    )

    return {
        "global_year": global_year,
        "effective_year": effective_year,
        "can_override": can_override,
        "override_active": override_active,
        "available_years": list(SchoolYear.objects.order_by("-name")) if can_override else [],
    }


def get_school_year_state(request):
    if request is None:
        return _compute_school_year_state(None)

    cached_state = getattr(request, REQUEST_STATE_CACHE_KEY, None)
    if cached_state is not None:
        return cached_state

    cached_state = _compute_school_year_state(request)
    setattr(request, REQUEST_STATE_CACHE_KEY, cached_state)
    return cached_state


def user_can_override_school_year(user):
    return bool(getattr(user, "is_authenticated", False) and (user.is_superuser or _user_has_any_group(user, {"garant_temataky"})))


def get_global_active_school_year(request=None):
    return get_school_year_state(request)["global_year"]


def get_effective_school_year(request):
    return get_school_year_state(request)["effective_year"]


def set_school_year_override(request, school_year_id):
    if not user_can_override_school_year(getattr(request, "user", None)):
        raise ValidationError("Nemáš oprávnění přepnout školní rok.")

    if not school_year_id:
        request.session.pop(SESSION_OVERRIDE_KEY, None)
        if hasattr(request, REQUEST_STATE_CACHE_KEY):
            delattr(request, REQUEST_STATE_CACHE_KEY)
        return

    school_year = SchoolYear.objects.filter(pk=school_year_id).first()
    if not school_year:
        raise ValidationError("Vybraný školní rok neexistuje.")

    request.session[SESSION_OVERRIDE_KEY] = school_year.id
    if hasattr(request, REQUEST_STATE_CACHE_KEY):
        delattr(request, REQUEST_STATE_CACHE_KEY)
