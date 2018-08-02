PYTHON ?= python3
REQ_PYTHON_MINOR_VERSION = 5
PREFIX ?= $(abspath .)
CONF_PATH = $(PREFIX)/conf.json

# to disable venv, set ENV_PATH to an empty value
ENV_PATH ?= $(PREFIX)/env
ifneq ($(strip $(ENV_PATH)),)
ENV_UPDATE_TIMESTAMP = $(ENV_PATH)/update_timestamp
else
ENV_UPDATE_TIMESTAMP =
endif

REQUIREMENTS_PATH ?= requirements.txt
MANAGE_PATH = $(PREFIX)/manage.sh
SRCDIR_PATH = $(PREFIX)/src
MAIN_CSS_PATH = $(SRCDIR_PATH)/tn2app/static/css/main.min.css

.PHONY: all reqs

all: $(ENV_UPDATE_TIMESTAMP) $(MAIN_CSS_PATH) $(MANAGE_PATH)
	@echo "Done! Don't forget to run ./manage.sh migrate!"

reqs:
	@ret=`${PYTHON} -c "import sys; print(int(sys.version_info[:2] >= (3, ${REQ_PYTHON_MINOR_VERSION})))"`; \
		if [ $${ret} -ne 1 ]; then \
			echo "Python 3.${REQ_PYTHON_MINOR_VERSION}+ required. Aborting."; \
			exit 1; \
		fi

ifneq ($(strip $(ENV_PATH)),)
$(ENV_PATH): | reqs
	@echo "Creating our virtualenv"
	${PYTHON} -m venv $(ENV_PATH) || \
		echo "Creation of our virtualenv failed. You probably need python3-venv."

$(ENV_UPDATE_TIMESTAMP): $(ENV_PATH) $(REQUIREMENTS_PATH)
	$(ENV_PATH)/bin/python -m pip install -r $(REQUIREMENTS_PATH)
	touch $@
endif

$(MAIN_CSS_PATH): src/tn2app/sass/main.scss $(wildcard src/tn2app/sass/_*.scss) $(ENV_PATH)
	sassc -t compressed $< $@

$(MANAGE_PATH): install/manage.sh.template
	sed -e "s#%CONF_PATH%#$(CONF_PATH)#g" \
		-e "s#%ENV_PATH%#$(ENV_PATH)#g" \
		-e "s#%SRCDIR_PATH%#$(SRCDIR_PATH)#g" \
		$< > $@ || (rm $@; exit 1)
	chmod +x $@

# Dev-related commands

.PHONY: watch migrate collectstatic test
collectstatic: $(MANAGE_PATH) $(MAIN_CSS_PATH)
	$(MANAGE_PATH) collectstatic --no-input

migrate: $(MANAGE_PATH)
	$(MANAGE_PATH) migrate

watch:
	find src/tn2app/sass/*.scss | entr make collectstatic

test: $(MANAGE_PATH)
	$(MANAGE_PATH) test
