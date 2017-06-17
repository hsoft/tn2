PYTHON ?= python3
REQ_PYTHON_MINOR_VERSION = 4
CONF_PATH ?= ./conf.json

.PHONY: reqs

all: manage.sh | env

env : | reqs
	@echo "Creating our virtualenv"
	${PYTHON} -m venv env
	./env/bin/python -m pip install -r requirements.freeze

reqs :
	@ret=`${PYTHON} -c "import sys; print(int(sys.version_info[:2] >= (3, ${REQ_PYTHON_MINOR_VERSION})))"`; \
		if [ $${ret} -ne 1 ]; then \
			echo "Python 3.${REQ_PYTHON_MINOR_VERSION}+ required. Aborting."; \
			exit 1; \
		fi
	@${PYTHON} -m venv -h > /dev/null || \
		echo "Creation of our virtualenv failed. If you're on Ubuntu, you probably need python3-venv."

manage.sh: $(CONF_PATH)
	sed -e "s#%CONF_PATH%#$(CONF_PATH)#g" install/manage.sh.template > $@ || (rm $@; exit 1)
	chmod +x $@

$(CONF_PATH):
	$(error $(CONF_PATH) file needed. Copy it from install/conf.json.example)
