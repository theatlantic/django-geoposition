from __future__ import unicode_literals

import json

from django import forms
from django.template.loader import render_to_string
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .conf import settings


class GeopositionLabeledTextInput(forms.TextInput):

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop('verbose_name')
        super(GeopositionLabeledTextInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        input_html = super(GeopositionLabeledTextInput, self).render(name, value, attrs)
        html = '<label for="%(id)s">%(verbose_name)s</label>%(input_html)s' % {
            'id': "id_%s" % name,
            'verbose_name': self.verbose_name.title(),
            'input_html': input_html,
        }
        return mark_safe(html)


class GeopositionWidget(forms.MultiWidget):
    template_name = 'geoposition/widgets/geoposition.html'

    def __init__(self, attrs=None, config=None):
        widgets = (
            GeopositionLabeledTextInput(verbose_name=_("latitude")),
            GeopositionLabeledTextInput(verbose_name=_("longitude")),
        )
        config = config or {}
        self._config = {}
        for k, v in six.iteritems(config):
            if isinstance(v, six.integer_types + six.string_types + (float, bool)):
                self._config[k] = v
            else:
                self._config[k] = json.dumps(v)
        super(GeopositionWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, six.text_type):
            return value.rsplit(',')
        if value:
            return [value.latitude, value.longitude]
        return [None, None]

    def get_config(self):
        config = {
            'map_widget_height': settings.MAP_WIDGET_HEIGHT or 500,
            'map_options': json.dumps(settings.MAP_OPTIONS),
            'marker_options': json.dumps(settings.MARKER_OPTIONS),
        }
        config.update(self._config)
        return config

    def get_context(self, name, value, attrs):
        # Django 1.11 and up
        context = super(GeopositionWidget, self).get_context(name, value, attrs)
        context['latitude'] = {
            'widget': context['widget']['subwidgets'][0],
            'label': _("latitude"),
        }
        context['longitude'] = {
            'widget': context['widget']['subwidgets'][1],
            'label': _("longitude"),
        }
        context['config'] = self.get_config()
        return context

    def format_output(self, rendered_widgets):
        # Django 1.10 and down
        return render_to_string('geoposition/widgets/geoposition.html', {
            'latitude': {
                'html': rendered_widgets[0],
                'label': _("latitude"),
            },
            'longitude': {
                'html': rendered_widgets[1],
                'label': _("longitude"),
            },
            'config': self.get_config(),
        })

    class Media:
        js = (
            '//maps.google.com/maps/api/js?key=%s' % settings.GOOGLE_MAPS_API_KEY,
            'geoposition/geoposition.js',
        )
        css = {
            'all': ('geoposition/geoposition.css',)
        }
