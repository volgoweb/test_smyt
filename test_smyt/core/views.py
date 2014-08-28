# -*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.generic import ListView
from .models import *
import json
from django.views.generic import View
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import modelform_factory

class BackboneView(View):
    model = factory.get_model_class('task')
    def queryset(self, request, **kwargs):
        return self.model.objects.all()

    def get(self, request, id = None, **kwargs):
        if id:
            obj = get_object_or_404(self.queryset(request, **kwargs), id = id)
            return self.get_object_detail(request, obj)
        else:
            return self.get_collection(request, **kwargs)

    def get_model_fields(self, obj):
        fields = {}
        for f in self.model._meta.fields:
            value = getattr(obj, f.name)
            if isinstance(value, datetime.date):
                value = value.strftime('%d.%m.%Y')
            fields[f.name] = value
        return fields

    def model_to_json(self, obj):
        fields = self.get_model_fields(obj)
        return json.dumps(fields)

    def get_object_detail(self, request, obj):
        return HttpResponse(self.model_to_json(obj), content_type = 'application/json')

    def get_collection(self, request, **kwargs):
        objs = self.queryset(request, **kwargs)
        data = []
        for obj in objs:
            data.append(self.get_model_fields(obj))
        return HttpResponse(json.dumps(data))

    @csrf_exempt
    def put(self, request, id = None, **kwargs):
        if id:
            obj = get_object_or_404(self.queryset(request), id = id)
            return self.update_object(request, obj)
        else:
            return self.add_object(request)

    def get_data_from_request(self, request):
        try:
            return json.loads(request.body if hasattr(request, 'body') else request.raw_post_data)
        except ValueError:
            return HttpResponseBadRequest('Parse JSON error.')

    @csrf_exempt
    def add_object(self, request):
        data = self.get_data_from_request(request)
        model_form = self.get_model_form(request, data = data)
        if model_form.is_valid():
            obj = model_form.save()
            return self.get_object_detail(request, obj)
        else:
            return HttpResponseBadRequest(json.dumps(model_form.errors), content_type='application/json')

    def update_object(self, request, obj):
        data = self.get_data_from_request(request)
        model_form = self.get_model_form(request, data = data, instance = obj)
        if model_form.is_valid():
            obj = model_form.save()
            return self.get_object_detail(request, obj)
        else:
            return HttpResponseBadRequest(json.dumps(model_form.errors), content_type='application/json')

    def get_model_form(self, request, data = None, instance = None):
        model_form = modelform_factory(self.model)
        return model_form(data, instance = instance)




class TasksList(ListView):
    model = factory.get_model_class('task')
    template = 'core/list_edit_in_place.html'
    context_object_name = 'models'

def tasks_list(request):
    return render(request, 'core/list_edit_in_place.html', {})

def get_task_collection(request):
    Task = factory.get_model_class('task')
    models = Task.objects.all()
    items = []
    for m in models:
        items.append({
            'id': m.id,
            'title': m.title,
            'priority': m.priority,
            'due_date': m.due_date.strftime('%d.%m.%Y'),
        })
    if request.GET.get('p') == 'count':
        return HttpResponse(models.count())

    data = json.dumps(items)
    return HttpResponse(data, mimetype = 'application/json')

def get_task(request, tid):
    Task = factory.get_model_class('task')
    model = Task.objects.filter(id = tid)
    data = json.dumps({
        'id': model.id,
        'title': model.title,
        'priority': model.priority,
        'due_date': model.due_date,
    })
    return HttpResponse(data, mimetype = 'application/json')
