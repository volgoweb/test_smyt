# -*- coding: utf-8 -*-
from django.db import models
import yaml
from datetime import datetime
from .utils import get_definition_file_path

class ModelClassFactory(object):
    def __init__(self, file_path, *args, **kwargs):
        self.file_path = file_path
        definition_text = open(self.file_path)
        self.definition_dict = self.convert_text_to_dict(definition_text)

    def get_all_classes(self):
        classes = []
        for class_name in self.definition_dict:
            classes.append(self.get_class(class_name))
        return classes

    def get_class(self, class_name):
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
        raise NotImplementedError()

    def get_fields(self, fields_definition):
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
        # TODO написать маппинг
        return models.IntegerField(verbose_name = field_definition.get('title'))

    def get_char_field(self, field_definition):
        return models.CharField(max_length = 254, verbose_name = field_definition.get('title'))

    def get_date_field(self, field_definition):
        return models.DateField(verbose_name = field_definition.get('title'))

class ModelClassFactoryYaml(ModelClassFactory):
    def convert_text_to_dict(self, definition_text):
        return yaml.load(definition_text)

file_path = get_definition_file_path()
factory = ModelClassFactoryYaml(file_path)
for cls in factory.get_all_classes():
    cls

