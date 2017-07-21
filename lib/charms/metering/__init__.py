from charmhelpers.core.unitdata import kv

CODE='juju.metering.status.code'
INFO='juju.metering.status.info'


def status():
    unit_data = kv()
    code = unit_data.get(CODE)
    message = unit_data.get(INFO)
    return code, message
