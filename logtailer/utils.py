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

import os
import tempfile

from datetime import datetime, timedelta

from django.conf import settings


def file_writable(a_file):
    return all([
        os.path.exists(a_file),
        os.path.isfile(a_file),
        os.access(a_file, os.W_OK)
    ])


def file_readable(a_file):
    return all([
        os.path.exists(a_file),
        os.path.isfile(a_file),
        os.access(a_file, os.R_OK)
    ])


def dir_writable(a_dir):
    return all([
        os.path.exists(a_dir),
        os.path.isdir(a_dir),
        os.access(a_dir, os.W_OK | os.X_OK)
    ])


def log_directory():
    log_dir = getattr(settings, 'LOGTAILER_LOG_DIR', '/var/log/logtailer')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, 0o0755)
        except OSError:
            log_dir = tempfile.mkdtemp()
    elif not dir_writable(log_dir):
        log_dir = tempfile.mkdtemp()
    return log_dir


def log_file():
    return getattr(settings, 'LOGTAILER_LOG_FILE',
                   os.path.join(log_directory(), "logtailer.log"))


def log_file_extensions():
    return getattr(settings, 'LOGTAILER_LOG_FILE_EXTENSIONS',
                   ".*\.(txt|TXT|log|LOG)$")


def logging_timer():
    return getattr(settings, 'LOGTAILER_LOGGING_TIMER',
                   os.path.join(tempfile.gettempdir(), "logtailer-timer"))


def logging_timer_exists():
    return file_writable(logging_timer())


def set_logging_timer():
    # 'touch' logging file
    with open(logging_timer(), 'a'):
        os.utime(logging_timer(), None)


def remove_logging_timer():
    if logging_timer_exists():
        os.remove(logging_timer())


def logging_timeout():
    return getattr(settings, 'LOGTAILER_TIMEOUT', 600)


def logging_timer_expired():
    if not logging_timer_exists():
        return True
    # Note: this is not timezone aware, but really doesn't need to be
    mtime = datetime.fromtimestamp(
        os.path.getmtime(logging_timer())) + \
        timedelta(seconds=logging_timeout())
    return datetime.now() > mtime
