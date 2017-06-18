PYTHON ?= python3
REQ_PYTHON_MINOR_VERSION = 4
CONF_PATH ?= ./conf.json
ENV_PATH ?= env

.PHONY: reqs migrate collectstatic

all: $(ENV_PATH) | migrate collectstatic

$(ENV_PATH) : | reqs
	@echo "Creating our virtualenv"
	${PYTHON} -m venv $(ENV_PATH) --system-site-packages
	$(ENV_PATH)/bin/python -m pip install -r requirements.freeze

reqs :
	@ret=`${PYTHON} -c "import sys; print(int(sys.version_info[:2] >= (3, ${REQ_PYTHON_MINOR_VERSION})))"`; \
		if [ $${ret} -ne 1 ]; then \
			echo "Python 3.${REQ_PYTHON_MINOR_VERSION}+ required. Aborting."; \
			exit 1; \
		fi
	@${PYTHON} -m venv -h > /dev/null || \
		echo "Creation of our virtualenv failed. If you're on Ubuntu, you probably need python3-venv."

migrate: manage.sh
	./manage.sh migrate

collectstatic: manage.sh
	./manage.sh collectstatic --no-input

manage.sh: $(CONF_PATH)
	sed -e "s#%CONF_PATH%#$(CONF_PATH)#g" -e "s#%ENV_PATH%#$(ENV_PATH)#g" install/manage.sh.template > $@ || (rm $@; exit 1)
	chmod +x $@

$(CONF_PATH):
	$(error $(CONF_PATH) file needed. Copy it from install/conf.json.example)
