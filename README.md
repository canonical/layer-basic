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

[charm-helpers]: https://pythonhosted.org/charmhelpers/
[layer-basic documentation]: https://charmsreactive.readthedocs.io/en/latest/layer-basic.html
