#!/usr/bin/make
PYTHON := /usr/bin/env python

all: lint test


lint:
	@flake8 $(wildcard hooks reactive unit_tests tests)
	@charm proof

unit_test:
	@echo Starting tests...
	tox
