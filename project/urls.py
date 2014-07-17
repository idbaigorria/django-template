from __future__ import absolute_import

from django.contrib import admin
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from rapidsms.backends.kannel.views import KannelBackendView
from rapidsms.contrib.httptester import urls

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # RapidSMS core URLs
    (r'^accounts/', include('rapidsms.urls.login_logout')),
    #url(r'^$', 'rapidsms.views.dashboard', name='rapidsms-dashboard'),
    # RapidSMS contrib app URLs
    (r'^httptester/', include('rapidsms.contrib.httptester.urls')),
    #(r'^locations/', include('rapidsms.contrib.locations.urls')),
    (r'^messagelog/', include('rapidsms.contrib.messagelog.urls')),
    (r'^messaging/', include('rapidsms.contrib.messaging.urls')),
    (r'^registration/', include('rapidsms.contrib.registration.urls')),

    # Third party URLs
    (r'^selectable/', include('selectable.urls')),

    # kannel backend urls
    url(r"^backend/kannel-usb0-smsc/$",
        KannelBackendView.as_view(backend_name="kannel-usb0-smsc")),
    url(r'^kannel/', include('rapidsms.backends.kannel.urls')),

    # public_lights
    url('^lights/', include('public_lights.urls', namespace='public_lights')),

    # rest
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
