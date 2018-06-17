import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from captcha.fields import CaptchaField
import registration.forms

from ..models import UserProfile
from ..util import sanitize_comment
from .base import BaseModelForm

__all__ = [
    'LoginForm', 'SignupForm', 'UserProfileForm', 'ContactForm',
    'UserSendMessageForm']


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Adresse e-mail")
    error_messages = dict(AuthenticationForm.error_messages,
        invalid_login="Mauvaise adresse e-mail et/ou mot de passe")


class SignupForm(registration.forms.RegistrationForm):
    field_order = ['username', 'email', 'password', 'password_confirm']

    captcha = CaptchaField(
        help_text="Pour confirmer que vous n'êtes pas un robot, entrez le <b>chiffre</b> (ex: 123) que vous voyez dans l'image",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Votre pseudo"
        self.fields['username'].help_text = "Uniquement des lettres, nombres et les caractères « . », « _ »."
        self.fields['email'].label = "Votre adresse e-mail"
        self.fields['password1'].label = "Votre mot de passe"
        self.fields['password2'].label = "Confirmez le mot de passe"

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[-\w.]+$', username):
            raise forms.ValidationError(
                "Uniquement des lettres, nombres et les caractères « . », "
                "« - » sont permis.")
        return username

    def clean_email(self):
        User = get_user_model()
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Il existe déjà un compte associé à ce courriel.")
        return email

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

