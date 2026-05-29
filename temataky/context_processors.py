from temataky.views.permissions import user_can_manage_all_temataky


def temataky_permissions(request):
    user = getattr(request, "user", None)
    can_manage_all_temataky = bool(
        user and user.is_authenticated and user_can_manage_all_temataky(user)
    )
    return {
        "can_manage_all_temataky": can_manage_all_temataky,
    }
