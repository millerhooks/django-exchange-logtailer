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

from logging.handlers import TimedRotatingFileHandler

from logtailer.utils import logging_timer_expired, log_file


class LogTailerHandler(TimedRotatingFileHandler, object):
    """
    Logs to temp file if logging timer file's last-modified datetime is within
    a given timeout. Logs are rotated on a daily basis at midnight (local time)
    and have, at most, 3 days worth of logging.

    This allows for verbose, e.g. DEBUG, logging to be dynamically enabled.

    A logging timer file is used so that multiple processes on the same
    machine, e.g. Django running inside Celery, can check whether to log.
    """

    # noinspection PyPep8Naming
    def __init__(self, filename=log_file(),
                 when='midnight', interval=1,
                 backupCount=3, encoding='utf-8',
                 delay=False, utc=False,
                 app=None):
        self.app = app
        super(LogTailerHandler, self).__init__(
            filename,
            when=when, interval=interval,
            backupCount=backupCount, encoding=encoding,
            delay=delay, utc=utc)

    def emit(self, record):
        """
        :param record:
        :type record: logging.LogRecord
        """

        if self.app is not None:
            record.__dict__.update(app=self.app)

        # Check elapse timer; log if still active
        if not logging_timer_expired():
            super(LogTailerHandler, self).emit(record)
