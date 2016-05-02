#!/usr/bin/make

TOX_VER = $(shell tox --version 2>/dev/null || echo "0.0")
TOX_VER_MAJOR := $(shell echo $(TOX_VER) | cut -f1 -d.)
TOX_VER_MINOR := $(shell echo $(TOX_VER) | cut -f2 -d.)
TOX_GT_1_8 := $(shell [ $(TOX_VER_MAJOR) -gt 1 -o \( $(TOX_VER_MAJOR) -eq 1 -a $(TOX_VER_MINOR) -ge 8 \) ] && echo true)

all: lint unit_test


.PHONY: clean
clean:
	@rm -rf .tox

.PHONY: tox_prereqs
tox_prereqs:
ifneq ($(TOX_GT_1_8),true)
        @echo "Pip installing tox"
        sudo apt-get install -y python-pip && sudo pip install -U 'tox>=1.8'
endif

.PHONY: lint
lint: tox_prereqs
	@tox --notest
	@PATH=.tox/py34/bin:.tox/py35/bin flake8 $(wildcard hooks reactive lib unit_tests tests)
	@charm proof

.PHONY: unit_test
unit_test: apt_prereqs
	@echo Starting tests...
	tox
