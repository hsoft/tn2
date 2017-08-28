import random

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.urls import reverse

from ..util import PermissiveURLField


__all__ = ['SponsorshipManager', 'Sponsorship']

class SponsorshipManager(models.Manager):
    def get_random_element(self, target):
        ids = list(self.filter(target=target).values_list('id', flat=True))
        if ids:
            sponsor = self.get(id=random.sample(ids, 1)[0])
            return (sponsor.image.url, sponsor.url)
        else:
            return None

    def get_random_main_page_element(self):
        result = self.get_random_element(Sponsorship.TARGET_MAIN_PAGE)
        if not result:
            result = (static('images/annoncez-270px.jpg'), reverse('page_sponsors'))
        return result

    def get_random_blog_element(self):
        result = self.get_random_element(Sponsorship.TARGET_BLOG)
        if not result:
            result = (static('images/annoncez-250px.jpg'), reverse('page_sponsors'))
        return result


class Sponsorship(models.Model):
    TARGET_NONE = 0
    TARGET_MAIN_PAGE = 1
    TARGET_BLOG = 2
    TARGET_CHOICES = [
        (TARGET_NONE, "Aucune"),
        (TARGET_MAIN_PAGE, "Page d'accueil"),
        (TARGET_BLOG, "Blog"),
    ]

    image = models.ImageField(upload_to='sponsors')
    url = PermissiveURLField()
    target = models.PositiveSmallIntegerField(
        db_index=True,
        choices=TARGET_CHOICES,
        verbose_name="Page cible",
    )

    objects = SponsorshipManager()

    def __str__(self):
        return "{} - {}".format(self.get_target_display(), self.url)


