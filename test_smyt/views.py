# -*- coding:utf-8 -*-
# from django.shortcuts import render
# from django.shortcuts import render_to_response
# from django.template import RequestContext
from django.http import Http404, HttpResponse
# from django.views.generic import ListView

def index(request):
    # from test_smyt.models import *
    # from django.conf import settings
    # import os
    # file_path = os.path.join(settings.PROJECT_DIR, 'model_classes.yaml')
    # assert False
    # cl = ModelClassFactoryYaml(file_path = file_path, class_name = 'task')
    # assert False

    return HttpResponse('Main page')

