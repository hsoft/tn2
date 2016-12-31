import html

from django.core.management.base import BaseCommand

from wordpress.models import WpV2Terms, WpV2TermTaxonomy, WpV2TermRelationships
from ...models import Article, ArticleCategory

class Command(BaseCommand):
    help = 'Imports article categories from our WP DB'

    def handle(self, *args, **options):
        wptaxes = WpV2TermTaxonomy.objects.filter(taxonomy='category')
        termid2taxid = {t.term_id: t.term_taxonomy_id for t in wptaxes.all()}
        taxid2cat = {}
        for wpcat in WpV2Terms.objects.filter(term_id__in=termid2taxid).all():
            if wpcat.slug == 'a-la-une':
                # We get rid of that category in the new site
                continue
            cat, created = ArticleCategory.objects.get_or_create(
                slug=wpcat.slug,
                defaults={
                    'title': html.unescape(wpcat.name),
                }
            )
            taxid2cat[termid2taxid[wpcat.term_id]] = cat
            if created:
                print("Created {}".format(cat))

        for article in Article.objects.all():
            slug = article.slug
            wpid = slug.split('-')[0]
            if not wpid.isdigit():
                # Not originating from wp
                continue
            wprels = WpV2TermRelationships.objects.filter(object_id=wpid, term_taxonomy_id__in=taxid2cat)
            print("Associating {} cats to article {}".format(wprels.count(), slug))
            for wprel in wprels.all():
                cat = taxid2cat[wprel.term_taxonomy_id]
                article.categories.add(cat)

