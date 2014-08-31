from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('test_smyt.core.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),
)
