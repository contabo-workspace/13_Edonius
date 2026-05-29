from core.models import UserProfile
from core.school_year_context import get_school_year_state


PROFILE_PHOTO_SESSION_KEY = "profile_photo_url"
MISSING_PROFILE_PHOTO = "__missing__"


def school_year_context(request):
    state = get_school_year_state(request)
    user = getattr(request, "user", None)

    profile_photo_url = None
    if user and user.is_authenticated:
        profile_photo_url = request.session.get(PROFILE_PHOTO_SESSION_KEY, MISSING_PROFILE_PHOTO)

        if profile_photo_url == MISSING_PROFILE_PHOTO:
            profile = UserProfile.objects.only("photo").filter(user_id=user.id).first()
            profile_photo_url = profile.photo.url if profile and profile.photo else ""
            request.session[PROFILE_PHOTO_SESSION_KEY] = profile_photo_url

        if not profile_photo_url:
            profile_photo_url = None

    return {
        "global_active_school_year": state["global_year"],
        "effective_school_year": state["effective_year"],
        "school_year_override_active": state["override_active"],
        "can_override_school_year": state["can_override"],
        "available_school_years": state["available_years"],
        "navbar_profile_photo_url": profile_photo_url,
    }
