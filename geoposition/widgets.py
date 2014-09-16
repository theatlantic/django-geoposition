from __future__ import unicode_literals

import copy
import json
from django import forms
from django.template.loader import render_to_string
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from .conf import DEFAULT_CONFIG


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
    def __init__(self, attrs=None, config=None):
        widgets = (
            GeopositionLabeledTextInput(verbose_name=_("latitude")),
            GeopositionLabeledTextInput(verbose_name=_("longitude")),
        )
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self.config.update(config)
        super(GeopositionWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if isinstance(value, six.text_type):
            return value.rsplit(',')
        if value:
            return [value.latitude, value.longitude]
        return [None,None]

    def format_output(self, rendered_widgets):
        serialized_config = {}
        for k, v in self.config.iteritems():
            if not isinstance(v, (long, int, six.text_type, float, bool)):
                v = json.dumps(v)
            serialized_config[k] = v

        return render_to_string('geoposition/widgets/geoposition.html', {
            'latitude': rendered_widgets[0],
            'longitude': rendered_widgets[1],
            'config': serialized_config,
        })

    class Media:
        js = (
            '//maps.google.com/maps/api/js?sensor=false',
            'geoposition/geoposition.js?v=1',
        )
        css = {
            'all': ('geoposition/geoposition.css',)
        }
