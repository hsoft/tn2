from django.db.models import Count
from django.forms.widgets import Select
from django.template import loader
from django.utils.safestring import mark_safe

from .models import PatternCreator, Pattern

class PatternSelect(Select):
    def render(self, name, value, attrs=None, renderer=None):
        nr = [(0, "Patron non répertorié")]
        if value:
            pattern = Pattern.objects.get(id=value)
            creator_id = pattern.creator_id
            self.choices = [(value, pattern.name)]
        else:
            creator_id = 0
            self.choices = nr
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


# It's not really a real Widget, but eh...
class UnrolledTwoColsSelect:
    template_name = 'widgets/unrolled_two_cols_select.html'

    def __init__(self, request, choices, argname):
        self.choices = list(choices)
        self.argname = argname
        self.reqparams = request.GET.copy()
        self.selected_value = self.reqparams.get(argname)
        if self.selected_value not in {str(val) for val, lbl in self.choices}:
            self.selected_value = None
        self.reqparams[argname] = ''
        self.reqparams['page'] = '1'

    def get_options(self):
        reqparams = self.reqparams.copy()
        for value, label in self.choices:
            reqparams[self.argname] = value
            isactive = str(value) == self.selected_value
            yield label, isactive, '?' + reqparams.urlencode()

    def get_neutral_href(self):
        return '?' + self.reqparams.urlencode()

    def get_context(self):
        return {
            'widget': self,
        }

    def render(self):
        result = loader.render_to_string(self.template_name, self.get_context())
        return mark_safe(result)

