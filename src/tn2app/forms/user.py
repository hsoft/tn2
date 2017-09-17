from django import forms

from captcha.fields import CaptchaField
import account.forms

from ..models import UserProfile
from ..util import sanitize_comment
from .base import BaseModelForm

__all__ = ['SignupForm', 'UserProfileForm', 'ContactForm', 'UserSendMessageForm']


class SignupForm(account.forms.SignupForm):
    field_order = ['username', 'email', 'password', 'password_confirm']

    captcha = CaptchaField(
        help_text="Pour confirmer que vous n'êtes pas un robot, entrez le <b>chiffre</b> (ex: 123) que vous voyez dans l'image",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Votre pseudo"
        self.fields['email'].label = "Votre adresse e-mail"
        self.fields['password'].label = "Votre mot de passe"
        self.fields['password_confirm'].label = "Confirmez le mot de passe"


class UserProfileForm(BaseModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'display_name', 'description', 'city', 'website', 'skill_level', 'sewing_machine',
            'avatar',
        ]
        widgets = {
            'city': forms.TextInput(),
            'sewing_machine': forms.TextInput(),
        }

    def clean_display_name(self):
        display_name = self.cleaned_data['display_name']
        if display_name.lower() != self.instance.display_name.lower():
            if UserProfile.objects.filter(display_name__iexact=display_name).exists():
                raise forms.ValidationError("Un autre utilisateur utilise déjà ce pseudo.")
        return display_name

    def clean_description(self):
        return sanitize_comment(self.cleaned_data['description'])


class ContactForm(forms.Form):
    required_css_class = 'required'

    name = forms.CharField(label="Votre nom", max_length=100)
    email = forms.EmailField(label="Votre email")
    subject = forms.CharField(label="Sujet de votre message", max_length=200)
    message = forms.CharField(label="Votre message", widget=forms.Textarea)


class UserSendMessageForm(forms.Form):
    required_css_class = 'required'

    message = forms.CharField(label="Votre message", widget=forms.Textarea)

