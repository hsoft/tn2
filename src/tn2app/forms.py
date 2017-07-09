import io

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile
from django.utils.text import slugify

from PIL import Image, ImageFile
from ckeditor.widgets import CKEditorWidget
from captcha.fields import CaptchaField
from easy_thumbnails.utils import exif_orientation
import account.forms

from .models import UserProfile, Discussion, Project, Pattern
from .util import dedupe_slug, sanitize_comment
from .widgets import PatternSelect

# http://stackoverflow.com/a/23575424
ImageFile.LOAD_TRUNCATED_IMAGES = True

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

    def clean_description(self):
        return sanitize_comment(self.cleaned_data['description'])


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


class CommentForm(forms.Form):
    comment = forms.CharField(
        label="Commentaire",
        widget=CKEditorWidget(config_name='restricted'),
        max_length=settings.COMMENT_MAX_LENGTH
    )

    def clean_comment(self):
        return sanitize_comment(self.cleaned_data['comment'])


class ProjectForm(BaseModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'pattern', 'target', 'domain', 'category', 'pattern_name', 'pattern_url',
            'description', 'blog_post_url', 'image1', 'image2', 'image3', 'image4'
        ]
        help_texts = {
            'title': "Choisissez un titre concis et explicite",
            'category': "Note : Toutes les réalisations à destination d'enfants appartiennent à la catégorie \"Enfants\". Nous n'acceptons plus de photos de mineurs de moins de 13 ans.",
            'pattern_name': "Si vous avez utilisé un patron ou un tutoriel pour réaliser votre projet, indiquez son nom ici.",
            'pattern_url': "Si le patron ou tutoriel utilisé est disponible sur un site internet, merci d'en indiquer l'adresse.",
            'blog_post_url': "Si vous avez publié ce projet sur votre blog, collez ici le lien direct vers l'article.",
        }

    pattern = forms.ModelChoiceField(
        queryset=Pattern.objects.all(),
        required=False,
        widget=PatternSelect,
        label="Patron",
        empty_label="Patron non répertorié",
        help_text="Si vous choisissez un patron répertorié, il n'est pas nécessaire de remplir les 5 champs qui suivent.",
    )

    def __init__(self, **kwargs):
        self.author = kwargs.pop('author', None)
        super().__init__(**kwargs)

    def validate_and_resize_image(self, image_uploaded_file):
        def cant_read():
            raise forms.ValidationError(
                "Impossible de lire l'image. Veuillez contacter les administrateurs de T&N"
            )

        if not isinstance(image_uploaded_file, UploadedFile):
            return image_uploaded_file
        result_bytes = io.BytesIO()
        try:
            with Image.open(image_uploaded_file) as image:
                # Ensure that our image has the proper orientation according to its EXIF data. For
                # this, we piggy-back on easy_thumbnails's own utility functions.
                new_image = exif_orientation(image)
                w, h = new_image.size
                if w > 630 or h > 630:
                    new_image.thumbnail((630, 630))
                try:
                    new_image.save(result_bytes, format=image.format)
                except OSError:
                    # could be a "cannot write mode P as JPEG" situation.
                    # let's try http://stackoverflow.com/a/21669827
                    try:
                        new_image.convert('RGB').save(result_bytes, format=image.format)
                    except OSError:
                        # Oh, screw that.
                        cant_read()
        except (FileNotFoundError, OSError):
            # Can't read the image, unset it
            cant_read()

        return SimpleUploadedFile(
            name=image_uploaded_file.name,
            content=result_bytes.getvalue(),
            content_type=image_uploaded_file.content_type,
        )


    def clean_image1(self):
        return self.validate_and_resize_image(self.cleaned_data['image1'])

    def clean_image2(self):
        return self.validate_and_resize_image(self.cleaned_data['image2'])

    def clean_image3(self):
        return self.validate_and_resize_image(self.cleaned_data['image3'])

    def clean_image4(self):
        return self.validate_and_resize_image(self.cleaned_data['image4'])

    def clean_target(self):
        result = self.cleaned_data['target']
        if not result:
            result = None
        return result

    def clean_domain(self):
        result = self.cleaned_data['domain']
        if not result:
            result = None
        return result

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('pattern'):
            if not all(cleaned_data.get(attr) for attr in {'target', 'domain', 'category'}):
                raise forms.ValidationError(
                    "Les champs Destinataire, Domaine et Catégorie sont nécessaires lorsque le "
                    "patron n'est pas répertorié"
                )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.author:
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

