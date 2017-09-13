PYTHON ?= python3
REQ_PYTHON_MINOR_VERSION = 4
VENV_ARGS ?=
DESTDIR ?= 
PREFIX ?= $(abspath .)
CONF_PATH = $(PREFIX)/conf.json
ENV_PATH = $(PREFIX)/env
REQUIREMENTS_PATH ?= requirements.txt
MANAGE_PATH = $(PREFIX)/manage.sh
SRCDIR_PATH = $(PREFIX)/src
MAIN_CSS_PATH = $(SRCDIR_PATH)/tn2app/static/css/main.min.css

.PHONY: reqs

all: $(DESTDIR)$(ENV_PATH) $(DESTDIR)$(MAIN_CSS_PATH) $(DESTDIR)$(MANAGE_PATH)
	@echo "Done! Don't forget to run ./manage.sh migrate!"

$(DESTDIR)$(ENV_PATH): | reqs
	@echo "Creating our virtualenv"
	${PYTHON} -m venv $(DESTDIR)$(ENV_PATH) $(VENV_ARGS)
	$(DESTDIR)$(ENV_PATH)/bin/python -m pip install -r $(REQUIREMENTS_PATH)

reqs:
	@ret=`${PYTHON} -c "import sys; print(int(sys.version_info[:2] >= (3, ${REQ_PYTHON_MINOR_VERSION})))"`; \
		if [ $${ret} -ne 1 ]; then \
			echo "Python 3.${REQ_PYTHON_MINOR_VERSION}+ required. Aborting."; \
			exit 1; \
		fi
	@${PYTHON} -m venv -h > /dev/null || \
		echo "Creation of our virtualenv failed. You probably need python3-venv."

$(DESTDIR)$(MAIN_CSS_PATH): src/tn2app/sass/main.scss $(wildcard src/tn2app/sass/_*.scss) $(DESTDIR)$(ENV_PATH)
	sassc -t compressed $< $@

$(DESTDIR)$(MANAGE_PATH): install/manage.sh.template
	sed -e "s#%CONF_PATH%#$(CONF_PATH)#g" \
		-e "s#%ENV_PATH%#$(ENV_PATH)#g" \
		-e "s#%SRCDIR_PATH%#$(SRCDIR_PATH)#g" \
		$< > $@ || (rm $@; exit 1)
	chmod +x $@

# Dev-related commands

.PHONY: watch migrate collectstatic

collectstatic: $(DESTDIR)$(MANAGE_PATH) $(MAIN_CSS_PATH)
	$(DESTDIR)$(MANAGE_PATH) collectstatic --no-input

migrate: $(DESTDIR)$(MANAGE_PATH)
	$(DESTDIR)$(MANAGE_PATH) migrate

watch:
	find src/tn2app/sass/*.scss | entr make collectstatic

# Install-related stuff

.PHONY: install_pre install

install_pre:
	$(PYTHON) -m compileall src
	mkdir -p $(DESTDIR)$(PREFIX)
	cp -r src $(DESTDIR)$(SRCDIR_PATH)

install: install_pre all

# Debian-related stuff

DEBVERSION ?= $(shell date +%Y%m%d)
DEBTIMESTAMP ?= $(shell date -R)
DEBWORKDIR ?= /tmp/tn2-$(DEBVERSION)

.PHONY: deb

$(DEBWORKDIR):	
	mkdir -p $@
	git archive HEAD | tar x -C $@

$(DEBWORKDIR)/debian/changelog: install/debian_changelog_template $(DEBWORKDIR) 
	sed -e "s#%VERSION%#$(DEBVERSION)#g" \
		-e "s#%TIMESTAMP%#$(DEBTIMESTAMP)#g" \
		$< > $@ || (rm $@; exit 1)

deb: $(DEBWORKDIR)/debian/changelog
	cd $(DEBWORKDIR) && dpkg-buildpackage -us -uc
