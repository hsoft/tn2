#!/bin/bash

export ENV_PATH=/tmp/tn2env

python3 -m venv --system-site-packages "$ENV_PATH"
"${ENV_PATH}/bin/pip" install -r requirements-non-system.txt

# pkg-resources is a dependency that is present in all virtualenvs and ends up in "pip freeze" call
# even when there's the "--local" flag. We filter it out from our freeze call.
"${ENV_PATH}/bin/pip" freeze --local | grep -v "^pkg-resources==" > requirements.freeze
