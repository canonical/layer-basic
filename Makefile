#!/usr/bin/make
PYTHON := /usr/bin/env python

all: lint test build


lint:
	@flake8 $(wildcard hooks unit_tests tests)
	@charm proof

unit_test:
	@echo Starting tests...
	tox
