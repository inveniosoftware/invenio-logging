# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module providing logging capabilities."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'flask-login>=0.3.2,<0.5.0',
    'httpretty>=0.8.14',
    'mock>=1.3.0',
    'pytest-invenio>=1.4.2',
    'iniconfig>=1.1.1',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
    'sentry': [
        'raven[flask]>=6',
    ],
    'sentry-sdk':[
        'sentry-sdk[flask]>=1.0.0'
    ]
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.7.0',
]

install_requires = [
    'invenio-celery>=1.2.4',
    'invenio-db>=1.0.12',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_logging', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-logging',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio logging',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-logging',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_logging_console'
            ' = invenio_logging.console:InvenioLoggingConsole',
            'invenio_logging_fs = invenio_logging.fs:InvenioLoggingFS',
            'invenio_logging_sentry'
            ' = invenio_logging.sentry:InvenioLoggingSentry',
        ],
        'invenio_base.api_apps': [
            'invenio_logging_console'
            ' = invenio_logging.console:InvenioLoggingConsole',
            'invenio_logging_fs = invenio_logging.fs:InvenioLoggingFS',
            'invenio_logging_sentry'
            ' = invenio_logging.sentry:InvenioLoggingSentry',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
    ],
)
