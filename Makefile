#!/usr/bin/make
PYTHON := /usr/bin/env python

all: lint test build


build: unit_test
	juju-compose -o ~/charms .

lint:
	@flake8 --exclude hooks/charmhelpers hooks unit_tests tests
	@charm proof

unit_test:
	@echo Starting tests...
	tox

test:
	@echo Starting Amulet tests...
	# coreycb note: The -v should only be temporary until Amulet sends
	# raise_status() messages to stderr:
	#   https://bugs.launchpad.net/amulet/+bug/1320357
	@juju test -v -p AMULET_HTTP_PROXY,AMULET_OS_VIP --timeout 2700
