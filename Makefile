#!/usr/bin/make
PYTHON := /usr/bin/env python

all: lint unit_test


lint:
	@flake8 $(wildcard hooks reactive lib unit_tests tests)
	@charm proof

unit_test:
	@echo Starting tests...
	tox
