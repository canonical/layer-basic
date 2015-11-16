# Overview

This is the base layer for all charms [built using layers][building].  It
provides all of the standard hooks, such as ``install``, ``config-changed``,
``upgrade-charm``, etc. and runs the [charms.reactive.main][charms.reactive]
loop for them.  It also bootstraps the [charm-helpers][] and [charms.reactive][]
libraries and all of their dependencies for use by the charm.


# Usage

To create a charm layer using this base layer, you need only include it in
a ``layer.yaml`` file:

```yaml
includes: ['layer:basic']
```

This will fetch this layer from [interfaces.juju.solutions][] and incorporate
it into your charm layer.  You can then add handlers under the ``reactive/``
directory.  Note that **any** file under ``reactive/`` will be expected to
contain handlers, whether as Python decorated functions or [executables][non-python]
using the [external handler protocol][].

You can also define Python libraries under ``lib/charms/X`` where ``X`` is a
package under the ``charms.`` namespace for your charm.  See [PyPI][pypi charms.X]
for what packages already exist under the ``charms.`` namespace.


# Layer Configuration

This layer does not currently support any configuration.


# Reactive States

This layer currently does not set any reactive states.


# Actions

This layer currently does not define any actions.


[building]: https://jujucharms.com/docs/devel/authors-charm-building
[charm-helpers]: https://pythonhosted.org/charmhelpers/
[charms.reactive]: https://pythonhosted.org/charms.reactive/
[interfaces.juju.solutions]: http://interfaces.juju.solutions/
[non-python]: https://pythonhosted.org/charms.reactive/#non-python-reactive-handlers
[external handler protocol]: https://pythonhosted.org/charms.reactive/charms.reactive.bus.html#charms.reactive.bus.ExternalHandler
[pypi charms.X]: https://pypi.python.org/pypi?%3Aaction=search&term=charms.&submit=search
