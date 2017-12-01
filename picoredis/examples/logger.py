# -*- coding: utf-8 -*-
"""A very simple file logging class."""

import time


DT_ISOFORMAT = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}"


class Logger:
    levels = ('error', 'warning', 'info', 'debug')

    def __init__(self, name, filename=None, level='info',
                 format="{timestamp}:{name}:{level}:{message}\n"):
        self.name = name
        self.format = format
        self.level = level
        if filename:
            self.filename = filename
        else:
            self.filename = name + '.log'

    def log(self, message, level='info'):
        if (level in self.levels and
                self.levels.index(level) <= self.levels.index(self.level)):
            try:
                with open(self.filename, 'a') as fp:
                    now = time.localtime()
                    fp.write(
                        self.format.format(
                            name=self.name,
                            level=level,
                            message=message.rstrip(),
                            timestamp=DT_ISOFORMAT.format(*now)))
            except OSError:
                pass
