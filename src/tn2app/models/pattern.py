from django.db import models

from ..util import PermissiveURLField


__all__ = ['PatternCreator', 'PatternCategory', 'Pattern']

class PatternCreator(models.Model):
    class Meta:
        app_label = 'tn2app'
        verbose_name = "Créateur de patrons"
        verbose_name_plural = "Créateurs de patrons"
        ordering = ['name']

    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    url = PermissiveURLField(
        blank=True,
        verbose_name="Site web"
    )

    def __str__(self):
        return self.name


class PatternCategory(models.Model):
    class Meta:
        app_label = 'tn2app'
        verbose_name = "Catégorie de patrons"
        verbose_name_plural = "Catégories de patrons"
        ordering = ['name']

    name = models.CharField(max_length=100, db_index=True, verbose_name="Nom")

    def __str__(self):
        return self.name


class Pattern(models.Model):
    class Meta:
        app_label = 'tn2app'
        verbose_name = "Patron"
        ordering = ['name']
        unique_together = [('creator', 'name')]

    TARGET_WOMAN = 1
    TARGET_MAN = 2
    TARGET_CHILD = 3
    TARGET_OTHER = 4
    TARGET_CHOICES = [
        (TARGET_WOMAN, "Femme"),
        (TARGET_MAN, "Homme"),
        (TARGET_CHILD, "Enfant"),
        (TARGET_OTHER, "Autre"),
    ]

    DOMAIN_SEWING = 1
    DOMAIN_KNITTING = 2
    DOMAIN_CROCHET = 3
    DOMAIN_NEEDLEWORK = 4
    DOMAIN_CHOICES = [
        (DOMAIN_SEWING, "Couture"),
        (DOMAIN_KNITTING, "Tricot"),
        (DOMAIN_CROCHET, "Crochet"),
        (DOMAIN_NEEDLEWORK, "Broderie"),
    ]

    creator = models.ForeignKey(
        PatternCreator,
        on_delete=models.PROTECT,
        related_name='patterns',
        verbose_name="Créateur",
    )
    name = models.CharField(max_length=100, db_index=True, verbose_name="Nom")
    url = PermissiveURLField(
        blank=True,
        verbose_name="Page web"
    )
    target = models.PositiveSmallIntegerField(
        db_index=True,
        choices=TARGET_CHOICES,
        verbose_name="Destinataire",
    )
    domain = models.PositiveSmallIntegerField(
        db_index=True,
        choices=DOMAIN_CHOICES,
        verbose_name="Domaine",
    )
    category = models.ForeignKey(
        PatternCategory,
        on_delete=models.PROTECT,
        verbose_name="Categorie",
    )
    is_free = models.BooleanField(default=False, db_index=True, verbose_name="Gratuit")
    is_jersey = models.BooleanField(default=False, db_index=True, verbose_name="Maille")

    def __str__(self):
        return self.name

    def get_legacy_category_id(self):
        if self.target == self.TARGET_MAN:
            return 13
        elif self.target == self.TARGET_CHILD:
            return 11
        elif self.domain in {self.DOMAIN_KNITTING, self.DOMAIN_CROCHET}:
            return 12
        elif self.domain == self.DOMAIN_NEEDLEWORK:
            return 14
        elif self.category.id <= 10:
            return self.category.id
        else:
            return 0

