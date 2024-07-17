#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  D  e  m  o  .  p  y 
#
#
__version__ = "MRSM_Demo IH240717a"
#
#
"""
Demo application to run on the Raspberry Pi MRSM controller: Main 
"""
#
# Copyright (C) 2024 Igor Hollaender, UM SAV
#
#-------------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#-------------------------------------------------------------------------------


# IH DEVELOPMENT NOTES
#-------------------------------------------------------------------------------
#


# TODOs
#-------------------------------------------------------------------------------

# BUGs
#
#   IH2407151 XXX
#
#-------------------------------------------------------------------------------


from typing import List
from PyQt6.QtWidgets import     \
    QApplication,           \
    QWidget,                \
    QPushButton           
from PyQt6.QtCore import        \
    QCommandLineOption,     \
    QCommandLineParser

import sys
import MRSM_Controller
from MRSM_Presentation import MRSM_Presentation


from MRSM_Globals import IsWaveShareDisplayEmulated
from MRSM_Globals import IsRaspberryPi5Emulated


class MSRM_Demo_QApplication(QApplication):
    """
    Main QApplication 
    """
    #IH240717 for debugging only
    QT_STYLES = ["windows", "windowsvista", "fusion", "macos"]

    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        
    def parseCommandLine(self):
        parser = QCommandLineParser()
        parser.addHelpOption()
        parser.addVersionOption()
                
        #IH240717 for debugging only
        style_option = QCommandLineOption(
            "s",
            "Use the specified Qt style, one of: " + ', '.join(self.QT_STYLES),
            "style"
        )
        parser.addOption(style_option)
                
        self.setApplicationVersion(__version__)

        parser.process(self)
                

#-------------------------------------------------------------------------------
MRSM_application = MSRM_Demo_QApplication(sys.argv)
MRSM_application.parseCommandLine()
MRSM_presentation = MRSM_Presentation()
MRSM_presentation.show()
MRSM_application.exec()

