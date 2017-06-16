PYTHON ?= python3
REQ_PYTHON_MINOR_VERSION = 4

.PHONY: reqs

all: conf.json | env

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

conf.json:
	$(error conf.json file needed at project root. Copy it from install/conf.json.example)
