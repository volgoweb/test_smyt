# -*- coding: utf-8 -*-
from django.db import models
import yaml
from datetime import datetime
from .utils import get_definition_file_path
from django.contrib import admin

class ModelFactory(object):
    '''
    Фабрика создания классов моделей.
    '''
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        definition_text = open(self.file_path)
        self.definition_dict = self.convert_text_to_dict(definition_text)

    def get_all_model_classes(self):
        '''
        Возвращает классы всех моделей.
        '''
        classes = []
        for class_name in self.definition_dict:
            classes.append(self.get_model_class(class_name))
        return classes

    def get_model_class(self, class_name):
        '''
        Возвращает класс указанной модели.
        '''
        cls_definition = self.definition_dict.get(class_name)

        fields = self.get_fields(cls_definition.get('fields'))
        if fields:
            class Meta():
                app_label = 'core'
                db_table = 'core_{0}'.format(class_name)

            fields.update({
                '__module__' : __name__,
                'Meta'       : Meta,
                'objects'    : models.Manager(),
            })

            cls = type(class_name, (models.Model,), fields)
            return cls
        else:
            return None

    def convert_text_to_dict(self, definition_text):
        '''
        Конвертация текста описания модели в словарь.
        !!! Метод обязательно переопределить при наследовании.
        '''
        raise NotImplementedError()

    def get_fields(self, fields_definition):
        '''
        Получение словаря описания полей модели {"имя поля": "класс поля"}
        '''
        fields = {}
        for fdefinition in fields_definition:
            ftype = fdefinition.get('type')
            method_name = 'get_{0}_field'.format(ftype)
            method = getattr(self, method_name, None)
            if callable(method):
                fields.update({
                    fdefinition.get('id'): method(fdefinition),
                })
        return fields

    def get_int_field(self, field_definition):
        '''
        Получение класса числового поля модели.
        '''
        return models.IntegerField(verbose_name = field_definition.get('title'))

    def get_char_field(self, field_definition):
        '''
        Получение класса текстового поля модели.
        '''
        return models.CharField(max_length = 254, verbose_name = field_definition.get('title'))

    def get_date_field(self, field_definition):
        '''
        Получение класса поля типа дата.
        '''
        return models.DateField(verbose_name = field_definition.get('title'))

    def get_admin_class(self, model_class):
        '''
        Получение класса для регистрации модели в админке.
        '''
        m_cls_name = model_class.__name__
        admin_class_name = '{0}Admin'.format(model_class.__name__)
        attrs = {
            'list_display': ['id',]
        }
        return type(admin_class_name, (admin.ModelAdmin,), attrs)

class ModelFactoryYaml(ModelFactory):
    '''
    Конвертация текста описания в yaml-формате модели в словарь.
    '''
    def convert_text_to_dict(self, definition_text):
        return yaml.load(definition_text)

# получаем путь к yaml-файлу описания моделей 
file_path = get_definition_file_path()
factory = ModelFactoryYaml(file_path)
# регистрируем все модели
for cls in factory.get_all_model_classes():
    cls

