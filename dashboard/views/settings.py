from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.urls import reverse

from core.models import UserProfile
from core.utils import get_user_shortcut
from core.context_processors import PROFILE_PHOTO_SESSION_KEY
from dashboard.forms import UserProfilePhotoForm


def settings_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    photo_form = UserProfilePhotoForm(instance=profile)
    display_name = request.user.get_full_name() or request.user.username
    photo_recently_saved = request.GET.get("photo_updated") == "1"
    context = {
        "display_name": display_name,
        "user_shortcut": get_user_shortcut(request.user),
        "profile": profile,
        "photo_form": photo_form,
        "photo_recently_saved": photo_recently_saved,
    }
    return render(request, "dashboard/settings.html", context)


def settings_photo_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method != "POST":
        return redirect("dashboard:settings")

    form = UserProfilePhotoForm(request.POST, request.FILES, instance=profile)
    if form.is_valid():
        form.save()
        request.session[PROFILE_PHOTO_SESSION_KEY] = profile.photo.url if profile.photo else ""
        messages.success(request, "Profilová fotka byla uložena.")
        return redirect(f"{reverse('dashboard:settings')}?photo_updated=1")

    display_name = request.user.get_full_name() or request.user.username
    context = {
        "display_name": display_name,
        "user_shortcut": get_user_shortcut(request.user),
        "profile": profile,
        "photo_form": form,
        "open_photo_modal": True,
    }
    return render(request, "dashboard/settings.html", context)


def settings_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Heslo bylo změněno.")
            return redirect("dashboard:settings")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "dashboard/settings_password.html", {"form": form})
