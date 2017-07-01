from django.db import models

from ..util import PermissiveURLField


__all__ = ['PatternCreator', 'Pattern']

class PatternCreator(models.Model):
    class Meta:
        app_label = 'tn2app'
        verbose_name = "Créateur de patrons"
        verbose_name_plural = "Créateurs de patrons"

    name = models.CharField(max_length=100, verbose_name="Nom")
    url = PermissiveURLField(
        blank=True,
        verbose_name="Site web"
    )

    def __str__(self):
        return self.name


class Pattern(models.Model):
    class Meta:
        app_label = 'tn2app'
        verbose_name = "Patron"

    creator = models.ForeignKey(PatternCreator)
    name = models.CharField(max_length=100, verbose_name="Nom")
    url = PermissiveURLField(
        blank=True,
        verbose_name="Page web"
    )
    is_free = models.BooleanField(default=False, db_index=True, verbose_name="Gratuit")

    def __str__(self):
        return self.name

