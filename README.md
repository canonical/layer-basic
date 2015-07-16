# Overview

This charm deploys the cloud-benchmarks.org website.

# Usage

Clone the repo and tell juju where to find it:

    mkdir -p ~/charms/trusty && cd ~/charms/trusty
    git clone https://github.com/juju-solutions/cloud-benchmarks-charm.git cloud-benchmarks
    export JUJU_REPOSITORY=~/charms

To deploy (requires postgres 9.4):

    juju deploy local:trusty/cloud-benchmarks
    juju deploy trusty/postgresql
    juju set postgresql version=9.4 pgdg=true
    juju add-relation cloud-benchmarks postgresql:db
    juju expose cloud-benchmarks

This charm can be scaled out behind haproxy:

    juju deploy haproxy
    juju add-relation haproxy cloud-benchmarks
    juju add-unit cloud-benchmarks

# Configuration Options

Github url from which to pull the webapp source code:

    juju set cloud-benchmarks repo=https://github.com/juju-solutions/cloud-benchmarks.org.git

The port on which to serve the website:

    juju set cloud-benchmarks port=6542
