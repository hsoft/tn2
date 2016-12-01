#!/bin/bash

{{ django_env }}/bin/pip install -U -r "{{ django_project_path }}/requirements.txt"

# pkg-resources is a dependency that is present in all virtualenvs and ends up in "pip freeze" call
# even when there's the "--local" flag. We filter it out from our freeze call.
{{ django_env }}/bin/pip freeze --local | grep -v "^pkg-resources==" > "{{ django_project_path }}/requirements.freeze"
