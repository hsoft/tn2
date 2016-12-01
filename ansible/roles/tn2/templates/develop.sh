#!/bin/bash

echo "You can open the debug site at:"
echo "http://{{ django_domain_name }}:8080"

cd {{ django_src_path }}
{{ django_env }}/bin/python manage.py runserver 0.0.0.0:8080
