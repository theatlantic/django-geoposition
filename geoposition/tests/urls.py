from django.conf.urls import url
from django.contrib import admin

import example.views

admin.autodiscover()


urlpatterns = [
    url(r'^$', example.views.poi_list),
    url(r'^admin/', admin.site.urls),
]
