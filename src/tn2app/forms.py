from django import forms
from django.utils.text import slugify

from django_comments.models import Comment
from django_comments.forms import COMMENT_MAX_LENGTH
from ckeditor.widgets import CKEditorWidget
from captcha.fields import CaptchaField
import account.forms

from .models import UserProfile, Discussion, Project
from .util import dedupe_slug


class SignupForm(account.forms.SignupForm):
    captcha = CaptchaField()


class BaseModelForm(forms.ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)


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


class NewDiscussionForm(BaseModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']

    def __init__(self, group, author, **kwargs):
        super().__init__(**kwargs)
        self.group = group
        self.author = author

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.group = self.group
        instance.author = self.author

        q = Discussion.objects.filter(group=self.group)
        instance.slug = dedupe_slug(slugify(instance.title), q)

        if commit:
            instance.save()

        return instance


class EditDiscussionForm(BaseModelForm):
    class Meta:
        model = Discussion
        fields = ['title', 'content']


class EditCommentForm(BaseModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

    comment = forms.CharField(
        label="Commentaire",
        widget=CKEditorWidget(config_name='restricted'),
        max_length=COMMENT_MAX_LENGTH
    )

class NewProjectForm(BaseModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'category', 'description', 'pattern_name', 'pattern_url', 'blog_post_url',
            'image1', 'image2', 'image3', 'image4', 'store_url'
        ]
        help_texts = {
            'title': "Choisissez un titre concis et explicite",
            'category': "Note : Toutes les réalisations à destination d'enfants appartiennent à la catégorie \"Enfants\". Nous n'acceptons plus de photos de mineurs de moins de 13 ans.",
            'pattern_name': "Si vous avez utilisé un patron ou un tutoriel pour réaliser votre projet, indiquez son nom ici.",
            'pattern_url': "Si le patron ou tutoriel utilisé est disponible sur un site internet, merci d'en indiquer l'adresse.",
            'blog_post_url': "Si vous avez publié ce projet sur votre blog, collez ici le lien direct vers l'article.",
            'store_url': "Indiquez l'adresse de la page correspondant à ce projet dans votre boutique Etsy, Dawanda, ALittleMarket...",
        }

    def __init__(self, author, **kwargs):
        super().__init__(**kwargs)
        self.author = author

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.author

        if commit:
            instance.save()

        return instance


class ContactForm(forms.Form):
    required_css_class = 'required'

    name = forms.CharField(label="Votre nom", max_length=100)
    email = forms.EmailField(label="Votre email")
    subject = forms.CharField(label="Sujet de votre message", max_length=200)
    message = forms.CharField(label="Votre message", widget=forms.Textarea)


class UserSendMessageForm(forms.Form):
    required_css_class = 'required'

    message = forms.CharField(label="Votre message", widget=forms.Textarea)

