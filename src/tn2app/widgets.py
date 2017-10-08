from django.db.models import Count
from django.forms.widgets import Select
from django.template import loader
from django.utils.safestring import mark_safe

from .models import PatternCreator, Pattern

class PatternSelect(Select):
    def render(self, name, value, attrs=None, renderer=None):
        nr = [(None, "Patron non répertorié")]
        if value:
            pattern = Pattern.objects.get(id=value)
            creator_id = pattern.creator_id
            self.choices = [(value, pattern.name)]
        else:
            creator_id = 0
            self.choices = nr
        creator_qs = PatternCreator.objects\
            .annotate(pattern_count=Count('patterns'))\
            .filter(pattern_count__gt=0)
        preselect = Select(choices=nr + list(creator_qs.values_list('id', 'name')))
        prefix_id = 'id_pattern_creator'
        prefix = preselect.render(name='', value=creator_id, attrs={'id': prefix_id})
        attrs = attrs or {}
        attrs['data-prefix-id'] = prefix_id
        result = super().render(name, value, attrs=attrs, renderer=renderer)
        return '\n'.join([prefix, result])


# It's not really a real Widget, but eh...
class AdHocWidget:
    def get_context(self):
        return {
            'widget': self,
        }

    def render(self):
        result = loader.render_to_string(self.template_name, self.get_context())
        return mark_safe(result)


class UnrolledSelect(AdHocWidget):
    template_name = 'widgets/unrolled_select.html'
    is_two_cols = False

    def __init__(self, reqparams, choices, argname):
        self.choices = list(choices)
        self.argname = argname
        self.reqparams = reqparams
        self.selected_value = self.reqparams.get(argname)
        if self.selected_value not in {str(val) for val, lbl in self.choices}:
            self.selected_value = None
        self.reqparams[argname] = ''
        self.reqparams['page'] = '1'

    def get_neutral_href(self):
        return '?' + self.reqparams.urlencode()

    def get_options(self):
        reqparams = self.reqparams.copy()
        for value, label in self.choices:
            reqparams[self.argname] = value
            isactive = str(value) == self.selected_value
            yield label, isactive, '?' + reqparams.urlencode()


class UnrolledTwoColsSelect(UnrolledSelect):
    is_two_cols = True


class CheckboxList(AdHocWidget):
    template_name = 'widgets/checkbox_list.html'

    def __init__(self, reqparams, choices):
        self.choices = list(choices)
        self.reqparams = reqparams
        self.reqparams['page'] = '1'

    def get_selected_options(self):
        return {v for v, _ in self.choices if self.reqparams.get(v, '0') == '1'}

    def get_options(self):
        selected = self.get_selected_options()
        for value, label in self.choices:
            current_value = value in selected
            target_value = not current_value
            reqparams = self.reqparams.copy()
            reqparams[value] = '1' if target_value else '0'
            yield label, current_value, '?' + reqparams.urlencode()

    def get_neutral_href(self):
        return '?' + self.reqparams.urlencode()

