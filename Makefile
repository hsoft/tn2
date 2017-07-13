PYTHON ?= python3
REQ_PYTHON_MINOR_VERSION = 4
CONF_PATH ?= $(abspath conf.json)
ENV_PATH ?= $(abspath env)
VENV_ARGS ?=
REQUIREMENTS_PATH ?= requirements.txt
MANAGE_PATH ?= ./manage.sh
SRCDIR_PATH = $(abspath src)
MAIN_CSS_PATH = $(SRCDIR_PATH)/tn2app/static/css/main.min.css

.PHONY: reqs migrate collectstatic watch

all: $(ENV_PATH) | migrate collectstatic

$(ENV_PATH) : | reqs
	@echo "Creating our virtualenv"
	${PYTHON} -m venv $(ENV_PATH) $(VENV_ARGS)
	$(ENV_PATH)/bin/python -m pip install -r $(REQUIREMENTS_PATH)

reqs :
	@ret=`${PYTHON} -c "import sys; print(int(sys.version_info[:2] >= (3, ${REQ_PYTHON_MINOR_VERSION})))"`; \
		if [ $${ret} -ne 1 ]; then \
			echo "Python 3.${REQ_PYTHON_MINOR_VERSION}+ required. Aborting."; \
			exit 1; \
		fi
	@${PYTHON} -m venv -h > /dev/null || \
		echo "Creation of our virtualenv failed. If you're on Ubuntu, you probably need python3-venv."

migrate: $(MANAGE_PATH)
	$(MANAGE_PATH) migrate

$(MAIN_CSS_PATH): $(SRCDIR_PATH)/tn2app/sass/main.scss $(wildcard $(SRCDIR_PATH)/tn2app/sass/_*.scss) $(ENV_PATH)
	$(ENV_PATH)/bin/sassc -t compressed $< $@

collectstatic: $(MANAGE_PATH) $(MAIN_CSS_PATH)
	$(MANAGE_PATH) collectstatic --no-input

watch:
	find $(SRCDIR_PATH)/tn2app/sass/*.scss | entr make collectstatic

$(MANAGE_PATH): $(CONF_PATH)
	sed -e "s#%CONF_PATH%#$(CONF_PATH)#g" \
		-e "s#%ENV_PATH%#$(ENV_PATH)#g" \
		-e "s#%SRCDIR_PATH%#$(SRCDIR_PATH)#g" \
		install/manage.sh.template > $@ || (rm $@; exit 1)
	chmod +x $@

$(CONF_PATH):
	$(error $(CONF_PATH) file needed. Copy it from install/conf.json.example)
