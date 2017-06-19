#!/bin/bash

export ENV_PATH=/tmp/tn2env
export VENV_ARGS=--system-site-packages

rm -rf $ENV_PATH
cd "{{ django_project_path }}"
make $ENV_PATH

# pkg-resources is a dependency that is present in all virtualenvs and ends up in "pip freeze" call
# even when there's the "--local" flag. We filter it out from our freeze call.
"${ENV_PATH}/bin/pip" freeze --local | grep -v "^pkg-resources==" > requirements.freeze
