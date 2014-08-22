# -*- coding: utf-8 -*-
import os

def get_definition_file_path():
    return os.path.join(os.path.dirname(__file__), 'model_classes.yaml')
