from subprocess import check_call

def add_metric(**metrics):
    """
    Report charm metrics.
    """
    cmd = ['add-metric']
    for key, value in metrics.items():
        cmd.append("%s=%s" % (key, value))

    check_call(cmd)
