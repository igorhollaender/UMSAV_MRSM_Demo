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
#   for __version__ , see MRSM_Globals
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
#   Installations on RIP:
#
#   ---------------
#   IH240722
#   To get rid of message: qt.qpa: Could not find the Qt platform plugin "wayland" in "",
#   I installed>
#       sudo apt install qt6-wayland
#   see
#   https://stackoverflow.com/questions/69994530/qt-qpa-plugin-could-not-find-the-qt-platform-plugin-wayland
#
#
#-------------------------------------------------------------------------------
#  On RPI, the python code resides here>
#
#   /home/um/Projekty_UM_ODD4/MRSM/code
#
#-------------------------------------------------------------------------------
#
#  For autostart apps in the desktop enviroment, use the Main Menu Editor
#
#      https://stackoverflow.com/questions/17939480/executing-a-script-after-the-user-has-logged-in-on-raspberry-pi/64957268#64957268
#
#   the autostart script is here>
#      /etc/xdg/lxsession/LXDE-pi/autostart
#  also see (for manual setup)
#      https://raspberry-projects.com/pi/pi-operating-systems/raspbian/auto-running-programs-gui#

# TODOs
#-------------------------------------------------------------------------------

# PROBLEMs
#
#   IH240722 Problem with installing PyQt6/QtMultimedia on RPI
#   Try using PySide6 as a replacement for PyQt6

#   IH240920 FIXED
#       IH240918 language setting is not working for Segmentation : implementation problem (cannot access language var variable)


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

from MRSM_Controller import MRSM_Controller
from MRSM_Presentation import MRSM_Presentation
from MRSM_TextContent import Language, LanguageAbbrev

from MRSM_Globals import (
        IsWaveShareDisplayEmulated,
        IsRaspberryPi5Emulated,
        VerboseLevel,
        __version__
        )

from MRSM_Utilities import error_message, debug_message

class MSRM_Demo_QApplication(QApplication):
    """
    Main QApplication 
    """
    
    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)
        
    def parseCommandLine(self):
        parser = QCommandLineParser()
        parser.addHelpOption()
        parser.addVersionOption()
        self.setApplicationVersion(__version__)

        # IH240918
        # language_dict = {Lan:Language.ENGLISH, 'SK':Language.SLOVAK, 'GE':Language.GERMAN}   
        language_dict = {langAbbrev.name :  langAbbrev.value  for langAbbrev in LanguageAbbrev}     
        language_option = QCommandLineOption(
            "l",
            f"Use the specified GUI language, one of: {list(language_dict.keys())}",
            "language",
            "EN"
        )
        parser.addOption(language_option)
                
        parser.process(self)

        self.app_language = language_dict.get(parser.value(language_option))
        if self.app_language is None:
            error_message(f'Invalid language: {parser.value(language_option)}. Using EN instead.')
            self.app_language = Language.ENGLISH
        

def finalizeApp():
    MRSM_controller.finalize()

#-------------------------------------------------------------------------------
MRSM_application = MSRM_Demo_QApplication(sys.argv)
MRSM_application.parseCommandLine()
MRSM_application.aboutToQuit.connect(finalizeApp)
MRSM_controller = MRSM_Controller()
MRSM_presentation = MRSM_Presentation(
        language=MRSM_application.app_language,
        hardwareController=MRSM_controller
        )
MRSM_presentation.show()
MRSM_application.exec()

