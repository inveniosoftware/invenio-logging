# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Minimal Flask application example.

SPHINX-START

First install Invenio-Logging, setup the application and load
fixture data by running:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh
   $ ./app-fixtures.sh

Next, start the development server:

.. code-block:: console

   $ export FLASK_APP=app.py FLASK_DEBUG=1
   $ flask run

and open the example application in your browser:

.. code-block:: console

    $ open http://127.0.0.1:5000/

You should now be able to see that an error message have been logged to the
console.

To reset the example application run:

.. code-block:: console

    $ ./app-teardown.sh

SPHINX-END
"""

from __future__ import absolute_import, print_function

from flask import Flask

from invenio_logging.console import InvenioLoggingConsole

# Create Flask application
app = Flask(__name__)
InvenioLoggingConsole(app)


@app.route('/')
def index():
    """Log error."""
    app.logger.error('Example error')
    return 'Welcome to Invenio-Logging!'
