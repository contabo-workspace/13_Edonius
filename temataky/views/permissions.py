from django.db.models import Q

from temataky.models import TematickyPlan


GROUP_NAMES_CACHE_KEY = "_edonius_group_name_set"


def _user_has_any_group(user, group_names):
    if not getattr(user, "is_authenticated", False):
        return False

    cached_names = getattr(user, GROUP_NAMES_CACHE_KEY, None)
    if cached_names is None:
        cached_names = set(user.groups.values_list("name", flat=True))
        setattr(user, GROUP_NAMES_CACHE_KEY, cached_names)

    return bool(cached_names.intersection(group_names))


def user_can_manage_all_temataky(user):
    return bool(getattr(user, "is_authenticated", False) and (user.is_superuser or _user_has_any_group(user, {"garant_temataky"})))


def user_can_create_temataky(user):
    return bool(
        getattr(user, "is_authenticated", False)
        and (user.is_superuser or _user_has_any_group(user, {"garant_temataky", "ucitel_temataky"}))
    )


def visible_temataky_queryset(user, school_year=None):
    base = TematickyPlan.objects.all()

    if school_year is not None:
        base = base.filter(predmet_ve_skolnim_roce__school_year=school_year)

    if not getattr(user, "is_authenticated", False):
        return base.none()
    if user_can_manage_all_temataky(user):
        return base
    return base.filter(Q(owner=user) | Q(ucitele=user)).distinct()
