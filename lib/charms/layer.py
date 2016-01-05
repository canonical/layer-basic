import yaml


class LayerOptions(dict):
    """
    Container for layer-specific options.

    Each layer can define options that it accepts in its ``layer.yaml`` file.
    These definitions are provided in [jsonschema](http://json-schema.org/)
    format, which is the same format that Juju Action parameters are defined.

    Each layer can then also set option values that other layers have defined.
    The option values are validated at charm build time, and are made available
    to the charm via this class as a dictionary.
    """
    def __init__(self, layer_name):
        """
        Load layer-specific options from ``layer.yaml``.

        If the ``options`` section is not available in ``layer.yaml``, it
        falls back to a separate YAML file based on the `layer_name`.

        :param str layer_name: The name of the layer whose options we want.
        """
        super(LayerOptions, self).__init__()
        with open('layer.yaml') as fp:
            layer_yaml = yaml.safe_load(fp)
        self.update(layer_yaml.get('options', {}).get(layer_name, {}))
