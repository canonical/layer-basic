#!/bin/sh

if (which python3 > /dev/null); then
    PYTHON=python3
elif (which python > /dev/null); then
    PYTHON=python
else
    PYTHON=python3
    apt-get install -y python3
fi

# Architecture dependent Python modules that need to be installed as
# debs. Pure Python packages should be preferred and embedded.
imports="
import yaml;
import tempita;
import apt;
import distro_info;
"
packages="
${PYTHON}-yaml
${PYTHON}-tempita
${PYTHON}-apt
${PYTHON}-distro-info
"
if ! ($PYTHON -c "${imports}" 2>/dev/null); then
    apt-get install -y ${packages}
fi

# The version of Python to be used to run hooks and actions is
# configured with the executable key in layer.yaml
PYTHON=`python -c "
import os;
import yaml;
layer = yaml.load(open('${CHARM_DIR}/layer.yaml'))
print(layer.get('executable', '${PYTHON}'))
"`

exec env JUJU_HOOK_NAME=${JUJU_HOOK_NAME:=`basename $0`} ${PYTHON} <<SCRIPT
import os
import sys

# Load modules from $CHARM_DIR/lib
sys.path.append(os.path.join(os.environ['CHARM_DIR'], 'lib'))

# This will load and run the appropriate @hook and other decorated
# handlers from $CHARM_DIR/reactive, $CHARM_DIR/hooks/reactive,
# and $CHARM_DIR/hooks/relations.
#
# See https://jujucharms.com/docs/stable/getting-started-with-charms-reactive
# for more information on this pattern.
from charms.reactive import main
main()
SCRIPT
