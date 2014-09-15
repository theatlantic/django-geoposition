# -*- coding: utf-8 -*-
from django.conf import settings
from appconf import AppConf


class GeopositionConf(AppConf):
    MAP_WIDGET_HEIGHT = 480
    MAP_OPTIONS = {}
    MARKER_OPTIONS = {}

    class Meta:
        prefix = 'geoposition'

DEFAULT_CONFIG = {
    'map_widget_height': settings.GEOPOSITION_MAP_WIDGET_HEIGHT,
    'map_options': settings.GEOPOSITION_MAP_OPTIONS,
    'marker_options': settings.GEOPOSITION_MARKER_OPTIONS,
}
