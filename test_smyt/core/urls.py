# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from .views import BackboneView
from django.views.decorators.csrf import ensure_csrf_cookie

urlpatterns = patterns('',
    url(r'^$', 'test_smyt.core.views.tasks_list', name='core__tasks_list'),
    url(r'^json/models-structure/$', 'test_smyt.core.views.get_models_structures', name='core__get_models_structures'),
    url(r'^json/(?P<model>\w+)/(?P<id>\d*)$', ensure_csrf_cookie(BackboneView.as_view()), name='core__backbone_view'),
)
