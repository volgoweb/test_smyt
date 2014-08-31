# -*- coding: utf-8 -*-
from django.contrib import admin
from models import *

file_path = get_definition_file_path()
factory = ModelFactoryYaml(file_path)
for mcls in factory.get_all_model_classes():
    adm_cls = factory.get_admin_class(mcls)
    admin.site.register(mcls, adm_cls);

