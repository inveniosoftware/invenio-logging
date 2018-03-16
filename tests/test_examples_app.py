# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test example app."""

import os
import signal
import subprocess
import time
from os.path import abspath, dirname, join

import pytest


@pytest.yield_fixture
def example_app():
    """Example app fixture."""
    current_dir = os.getcwd()

    # Go to example directory
    project_dir = dirname(dirname(abspath(__file__)))
    exampleappdir = join(project_dir, 'examples')
    os.chdir(exampleappdir)

    # Setup application
    assert subprocess.call('./app-setup.sh', shell=True) == 0

    # Setup fixtures
    assert subprocess.call('./app-fixtures.sh', shell=True) == 0

    # Start example web app
    cmd = 'FLASK_APP=app.py flask run --debugger -p 5001'
    webapp = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              preexec_fn=os.setsid, shell=True)
    time.sleep(5)
    # return webapp
    yield webapp

    # Stop server
    os.killpg(webapp.pid, signal.SIGTERM)

    # Tear down example app
    subprocess.call('./app-teardown.sh', shell=True)

    # Return to the original directory
    os.chdir(current_dir)


def test_example_app(example_app):
    """Test example app."""
    # Testing get index page
    cmd = 'curl http://127.0.0.1:5001/'
    output = subprocess.check_output(cmd, shell=True).decode("utf-8")
    assert 'Welcome to Invenio-Logging!' == output
