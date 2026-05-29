from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Uživatel",
    )
    photo = models.ImageField(
        upload_to="users/photos/",
        blank=True,
        null=True,
        verbose_name="Profilová fotka",
    )

    class Meta:
        ordering = ["user__username"]
        verbose_name = "Uživatelský profil"
        verbose_name_plural = "Uživatelské profily"

    def __str__(self):
        return self.user.get_username()
