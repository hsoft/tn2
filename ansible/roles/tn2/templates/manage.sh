#!/bin/bash

export TN2_CONF_PATH="{{ django_jsonsettings_path }}"
cd {{ django_src_path }}
{{ django_env }}/bin/python manage.py $@
