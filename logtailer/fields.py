# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2018 Boundless Spatial
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from __future__ import unicode_literals

import os
import logging

from django.db import models
from django import forms

from logtailer.utils import log_directory

logger = logging.getLogger(__name__)


# partially culled from https://stackoverflow.com/questions/7439336
class DynamicFilePathField(models.FilePathField):

    def __init__(self, *args, **kwargs):
        super(DynamicFilePathField, self).__init__(*args, **kwargs)
        if callable(self.path):
            self.pathfunc, self.path = self.path, self.path()
        if callable(self.match):
            self.matchfunc, self.match = self.match, self.match()

    def get_prep_value(self, value):
        value = super(DynamicFilePathField, self).get_prep_value(value)

        # Only keep the relative path to base dir
        if value and value.strip().startswith(log_directory()):
            value = os.path.relpath(value, log_directory().rstrip(os.sep))

        return value

    # noinspection PyUnusedLocal
    def from_db_value(self, value, expression, connection, context):
        a_file = self.to_python(value)
        if a_file:
            log_file = os.path.join(log_directory(), a_file)
            if os.path.exists(log_file):
                return log_file
        return a_file

    def deconstruct(self):
        name, path, args, kwargs = \
            super(DynamicFilePathField, self).deconstruct()
        if hasattr(self, "pathfunc"):
            kwargs['path'] = self.pathfunc
        if hasattr(self, "matchfunc"):
            kwargs['match'] = self.matchfunc
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        defaults = {
            'path': self.path,
            'match': self.match,
            'recursive': self.recursive,
            'form_class': forms.FilePathField,
            'allow_files': self.allow_files,
            'allow_folders': self.allow_folders,
        }
        defaults.update(kwargs)
        return super(DynamicFilePathField, self).formfield(**defaults)
