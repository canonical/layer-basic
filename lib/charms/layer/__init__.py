import os
from importlib import import_module
from pathlib import Path


class LayerOptions(dict):
    def __init__(self, layer_file, section=None):
        import yaml  # defer, might not be available until bootstrap
        with open(layer_file) as f:
            layer = yaml.safe_load(f.read())
        opts = layer.get('options', {})
        if section and section in opts:
            super(LayerOptions, self).__init__(opts.get(section))
        else:
            super(LayerOptions, self).__init__(opts)


def options(section=None, layer_file=None):
    if not layer_file:
        base_dir = os.environ.get('JUJU_CHARM_DIR', os.getcwd())
        layer_file = os.path.join(base_dir, 'layer.yaml')

    return LayerOptions(layer_file, section)


def import_layer_libs():
    """
    Ensure that all layer libraries are imported.

    This makes it possible to do the following:

        from charms import layer

        layer.foo.do_foo_thing()

    Note: This function must be called after bootstrap.
    """
    for module_file in Path('lib/charms/layer').glob('*'):
        module_name = module_file.stem
        if module_name in ('__init__', 'basic', 'execd') or not (
            module_file.suffix == '.py' or module_file.is_dir()
        ):
            continue
        import_module('charms.layer.{}'.format(module_name))
