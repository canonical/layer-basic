from charms import layer
from charms.reactive import trace

if layer.options.get('basic', 'trace'):
    trace.install_tracer(trace.LogTracer())
