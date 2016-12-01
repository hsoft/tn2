#!/bin/bash

cd {{ django_src_path }}
{{ django_env }}/bin/python manage.py $@
