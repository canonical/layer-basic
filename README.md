# Overview
<a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="Apache 2.0 License"></a>

This is the base layer for all reactive Charms. It provides all of the standard
Juju hooks and starts the reactive framework when these hooks get executed. It
also bootstraps the [charm-helpers][] and `charms.reactive` libraries, and all
of their dependencies for use by the Charm.

# Usage

Go read the [layer-basic documentation][] for more info on how to use this
layer. It is now hosted together with the charms.reactive documentation in order
to reduce the amount of places a charmer needs to search for info.

# Python Versions, Built charms and what they can run on.

Due to major backwards incompatibilities between Python 3.10 and previous
versions, there is a compatibility break between Python 3.8 (focal) and earlier
versions of Python.  Why Python 3.8 rather than 3.10?  Mostly due to all of the
incompatibilities being deprecated and available in Python 3.8, so the ability
of authors to test at that version.

As the charmhub.io now offers a place to build reactive charms on a per series
('base') and architecture basis, layer-basic supports *at least* Python 3.5 to
Python 3.10.  However, a charm *built* on Python 3.5 won't work on Python 3.8
and vice-versa.  The objective going forwards is to build the charm for the
*base* that the charm will run on.

[charm-helpers]: https://pythonhosted.org/charmhelpers/
[layer-basic documentation]: https://charmsreactive.readthedocs.io/en/latest/layer-basic.html
