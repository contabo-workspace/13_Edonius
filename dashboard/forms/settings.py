from django import forms

from core.models import UserProfile


class UserProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["photo"].required = False
        self.fields["photo"].help_text = "Nahraj novou profilovou fotku."
