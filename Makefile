#!/usr/bin/make
PYTHON := /usr/bin/env python

all: lint test build


build: unit_test
ifndef JUJU_REPOSITORY
	$(error JUJU_REPOSITORY must be defined)
endif
	charm-build .

lint:
	@flake8 $(wildcard hooks unit_tests tests)
	@charm proof

unit_test:
	@echo Starting tests...
	tox
