# -*- coding: utf-8 -*-
import os
from django.db import models

def get_definition_file_path():
    return os.path.join(os.path.dirname(__file__), 'model_classes.yaml')

def get_model_field_class_for_js(field):
    if type(field) is models.IntegerField:
        return 'integer'
    elif type(field) is models.CharField:
        return 'char'
    elif type(field) is models.DateField:
        return 'date'
    elif type(field) is models.AutoField:
        return 'integer'

