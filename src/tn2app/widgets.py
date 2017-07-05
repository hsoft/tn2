from django.forms.widgets import Select

from .models import PatternCreator

class PatternSelect(Select):
    def render(self, name, value, attrs=None, renderer=None):
        nr = [(0, "Patron non répertorié")]
        preselect = Select(choices=nr + list(PatternCreator.objects.values_list('id', 'name')))
        prefix_name = '{}-prefix'.format(name)
        prefix = preselect.render(prefix_name, None)
        attrs = attrs or {}
        attrs['data-prefix-name'] = prefix_name
        result = super().render(name, value, attrs=attrs, renderer=renderer)
        return '\n'.join([prefix, result])

