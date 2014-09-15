from __future__ import unicode_literals

import copy
import json
from django import forms
from django.template.loader import render_to_string
from django.utils import six
from django.utils.translation import ugettext_lazy as _
from .conf import DEFAULT_CONFIG


class GeopositionWidget(forms.MultiWidget):
    def __init__(self, attrs=None, config=None):
        widgets = (
            forms.TextInput(),
            forms.TextInput(),
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
            'latitude': {
                'html': rendered_widgets[0],
                'label': _("latitude"),
            },
            'longitude': {
                'html': rendered_widgets[1],
                'label': _("longitude"),
            },
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
