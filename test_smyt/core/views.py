# -*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.generic import ListView
from .models import *
from .utils import *
import json
from django.views.generic import View
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import modelform_factory

def tasks_list(request):
    '''
    Вывод базовой страницы списка моделей
    '''
    return render(request, 'core/models_list.html', {})

def get_models_structures(request):
    '''
    Получение структуры всех моделей в json формате.
    '''
    if not request.is_ajax():
        return

    structure = {}
    for cls in factory.get_all_model_classes():
        fields = cls._meta.fields
        cls_name = cls.__name__
        structure[cls_name] = {}
        for f in fields:
            structure[cls_name].update({
                f.name: get_model_field_class_for_js(f),
            })
    return HttpResponse(json.dumps(structure), mimetype = 'application/json')

class BackboneView(View):
    '''
    Представления для обработки аяксов запросов от backbone моделей и коллекций.
    '''
    def dispatch(self, request, *args, **kwargs):
        if 'model' in kwargs:
            model_name = str(kwargs.get('model'))
            self.model = factory.get_model_class(model_name)

        return super(BackboneView, self).dispatch(request, *args, **kwargs)

    def queryset(self, request, **kwargs):
        return self.model.objects.all()

    def get(self, request, id = None, **kwargs):
        '''
        Обработка http-запросов метода get.
        Возвращает либо объект модели, либо список объектов.
        '''
        if id:
            obj = get_object_or_404(self.queryset(request, **kwargs), id = id)
            return self.get_object_detail(request, obj)
        else:
            return self.get_collection(request, **kwargs)

    def get_model_fields(self, obj):
        '''
        Возвращает словарь значений полей модели.
        '''
        fields = {}
        for f in self.model._meta.fields:
            value = getattr(obj, f.name)
            if isinstance(value, datetime.date):
                value = value.strftime('%d.%m.%Y')
            fields[f.name] = value
        return fields

    def model_to_json(self, obj):
        '''
        Конвертация словаря значений модели в json формат.
        '''
        fields = self.get_model_fields(obj)
        return json.dumps(fields)

    def get_object_detail(self, request, obj):
        '''
        Возвращает объект модели в json-формате.
        '''
        return HttpResponse(self.model_to_json(obj), content_type = 'application/json')

    def get_collection(self, request, **kwargs):
        '''
        Возвращает список объектов указанной в запросе модели в json-формате.
        '''
        objs = self.queryset(request, **kwargs)
        data = []
        for obj in objs:
            data.append(self.get_model_fields(obj))
        return HttpResponse(json.dumps(data))

    def put(self, request, id = None, **kwargs):
        '''
        Общий метод сохранения существующего или создание нового объекта модели.
        '''
        if id:
            obj = get_object_or_404(self.queryset(request), id = id)
            return self.update_object(request, obj)
        else:
            return self.add_object(request)

    def get_data_from_request(self, request):
        '''
        Извлекает из request словарь полученных от backbone значений полей модели и возвращает его.
        '''
        try:
            return json.loads(request.body if hasattr(request, 'body') else request.raw_post_data)
        except ValueError:
            return HttpResponseBadRequest('Parse JSON error.')

    def add_object(self, request):
        '''
        Создание новой модели.
        '''
        data = self.get_data_from_request(request)
        model_form = self.get_model_form(request, data = data)
        if model_form.is_valid():
            obj = model_form.save()
            return self.get_object_detail(request, obj)
        else:
            return HttpResponseBadRequest(json.dumps(model_form.errors), content_type='application/json')

    def update_object(self, request, obj):
        '''
        Изменение существующей модели.
        '''
        data = self.get_data_from_request(request)
        model_form = self.get_model_form(request, data = data, instance = obj)
        if model_form.is_valid():
            obj = model_form.save()
            return self.get_object_detail(request, obj)
        else:
            return HttpResponseBadRequest(json.dumps(model_form.errors), content_type='application/json')

    def get_model_form(self, request, data = None, instance = None):
        '''
        Получение формы текущей модели.
        '''
        model_form = modelform_factory(self.model)
        return model_form(data, instance = instance)
