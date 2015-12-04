# Overview

This is the base layer for all charms [built using layers][building].  It
provides all of the standard Juju hooks and runs the
[charms.reactive.main][charms.reactive] loop for them.  It also bootstraps the
[charm-helpers][] and [charms.reactive][] libraries and all of their
dependencies for use by the charm.

# Usage

To create a charm layer using this base layer, you need only include it in
a `layer.yaml` file:

```yaml
includes: ['layer:basic']
```

This will fetch this layer from [interfaces.juju.solutions][] and incorporate
it into your charm layer.  You can then add handlers under the `reactive/`
directory.  Note that **any** file under `reactive/` will be expected to
contain handlers, whether as Python decorated functions or [executables][non-python]
using the [external handler protocol][].

You can also define Python libraries under `lib/charms/X` where `X` is a
package under the `charms.` namespace for your charm.  See [PyPI][pypi charms.X]
for what packages already exist under the `charms.` namespace.

# Hooks

This layer provides hooks that other layers can react to using the decorators
of the [charms.reactive][] library:

  * `config-changed`
  * `install`
  * `leader-elected`
  * `leader-settings-changed`
  * `start`
  * `stop`
  * `upgrade-charm`
  * `update-status`

Other hooks are not implemented at this time. A new layer can implement storage
or relation hooks in their own layer by putting them in the `hooks` directory.

**Note:** Because `update-status` is invoked every 5 minutes, you should take
care to ensure that your reactive handlers only invoke expensive operations
when absolutely necessary.  It is recommended that you use helpers like
[`@only_once`][], [`@when_file_changed`][], and [`data_changed`][] to ensure
that handlers run only when necessary.

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
[`@only_once`]: https://pythonhosted.org/charms.reactive/charms.reactive.decorators.html#charms.reactive.decorators.only_once
[`@when_file_changed`]: https://pythonhosted.org/charms.reactive/charms.reactive.decorators.html#charms.reactive.decorators.when_file_changed
[`data_changed`]: https://pythonhosted.org/charms.reactive/charms.reactive.helpers.html#charms.reactive.helpers.data_changed
