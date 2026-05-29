def get_user_shortcut(user):
    teacher_profile = getattr(user, "teacher_profile", None)
    if teacher_profile and teacher_profile.shortcut:
        return teacher_profile.shortcut

    first_name = (user.first_name or "").strip()
    last_name = (user.last_name or "").strip()
    username = (user.username or "").strip()

    if last_name and first_name:
        return f"{last_name[0].upper()}{first_name[0].lower()}"
    if last_name:
        return (last_name[:2].capitalize() if len(last_name) > 1 else last_name.upper())
    if first_name:
        return (first_name[:2].capitalize() if len(first_name) > 1 else first_name.upper())
    if username:
        return (username[:2].capitalize() if len(username) > 1 else username.upper())
    return "??"


def get_user_display_with_shortcut(user):
    full_name = f"{(user.last_name or '').strip()} {(user.first_name or '').strip()}".strip()
    if not full_name:
        full_name = user.username
    return f"{full_name} ({get_user_shortcut(user)})"
