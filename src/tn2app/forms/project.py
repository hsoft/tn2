import io

from django import forms
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile

from PIL import Image, ImageFile

from ..models import Project, Pattern
from ..util import exif_orientation
from ..widgets import PatternSelect
from .base import BaseModelForm

__all__ = ['ProjectForm']

# http://stackoverflow.com/a/23575424
ImageFile.LOAD_TRUNCATED_IMAGES = True

class ProjectForm(BaseModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'pattern', 'pattern_name', 'pattern_url', 'target', 'domain', 'category',
            'description', 'blog_post_url', 'image1', 'image2', 'image3', 'image4'
        ]
        help_texts = {
            'title': "Choisissez un titre concis et explicite",
            'target': "Note sur le destinataire \"Enfant\" : Nous n'acceptons pas de photos de mineurs de moins de 13 ans.",
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
        help_text="Si vous choisissez un patron répertorié, il n'est pas nécessaire de remplir " \
            "les 2 champs qui suivent. Les champs Destinataire, Domaine et Catégorie sont " \
            "automatiquement mis à jour selon le patron choisi, mais vous pouvez quand même " \
            "modifier ces champs si nécessaire.",
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.author:
            instance.author = self.author

        if commit:
            instance.save()

        return instance

