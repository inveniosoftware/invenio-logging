# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Compatibility layer for dealing with Sentry 6.x."""

from __future__ import absolute_import, print_function

from flask import current_app
from flask_login import current_user
from raven.contrib.flask import Sentry


class Sentry6(Sentry):
    """Compatibility layer for Sentry."""

    def get_user_info(self, request):
        """Implement custom getter."""
        if not current_user.is_authenticated:
            return {}

        user_info = {
            'id': current_user.get_id(),
        }

        if 'SENTRY_USER_ATTRS' in current_app.config:
            for attr in current_app.config['SENTRY_USER_ATTRS']:
                if hasattr(current_user, attr):
                    user_info[attr] = getattr(current_user, attr)

        return user_info
