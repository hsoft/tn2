from django.db.models import Count
from django.forms.widgets import Select

from .models import PatternCreator, Pattern

class PatternSelect(Select):
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            pattern = Pattern.objects.get(id=value)
            creator_id = pattern.creator_id
            self.choices = [(value, pattern.name)]
        else:
            creator_id = 0
        nr = [(0, "Patron non répertorié")]
        creator_qs = PatternCreator.objects\
            .annotate(pattern_count=Count('pattern'))\
            .filter(pattern_count__gt=0)
        preselect = Select(choices=nr + list(creator_qs.values_list('id', 'name')))
        prefix_id = 'id_pattern_creator'
        prefix = preselect.render(name='', value=creator_id, attrs={'id': prefix_id})
        attrs = attrs or {}
        attrs['data-prefix-id'] = prefix_id
        result = super().render(name, value, attrs=attrs, renderer=renderer)
        return '\n'.join([prefix, result])

