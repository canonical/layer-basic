# Overview

This charm deploys the cloud-benchmarks.org website.

# Usage

To deploy (requires postgres 9.4):

    juju deploy cloud-benchmarks
    juju deploy postgresql
    juju set postgresql version=9.4
    juju add-relation cloud-benchmarks postgresql

This charm can be scaled out behind haproxy:

    juju deploy haproxy
    juju add-relation haproxy cloud-benchmarks
    juju add-unit cloud-benchmarks

# Configuration Options

Github url from which to pull the webapp source code:

    juju set cloud-benchmarks repo=https://github.com/juju-solutions/cloud-benchmarks.org.git

The port on which to serve the website:

    juju set cloud-benchmarks port=6542
