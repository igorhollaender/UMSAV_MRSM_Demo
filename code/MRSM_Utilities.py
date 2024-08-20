#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  U  t  i  l  i  t  i  e  s  .  p  y 
#
#
#      Last update: IH240819
#-------------------------------------------------------------------------------

import time

from MRSM_Globals import VerboseLevel

from PyQt6.QtCore import (
    QTimer, 
    pyqtSignal,
    pyqtSlot
    )

def error_message(m):
    if VerboseLevel>0:
        print(m)
    
def debug_message(m):
    if VerboseLevel>1:
        print(f"MRSM debug: {time.asctime()}: {m}")


class TimerIterator(QTimer):
    """
    Based on source from
    https://stackoverflow.com/questions/68586377/iterate-with-an-interval-timer

    """
    value_changed = pyqtSignal()

    def __init__(self, values=None, parent=None):
        super().__init__(parent)
        self._values = []
        # self.timeout.connect(self.handle_timeout)
        self.values = values or []

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values
        self.setProperty("iterator", iter(self.values))

    def handle_timeout(self):
        try:
            value = next(self.property("iterator"))
        except StopIteration:
            self.stop()
        else:
            self.value_changed.emit(value)

