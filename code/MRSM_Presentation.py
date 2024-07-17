#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  P  r  e  s  e  n  t  a  t  i  o  n  .  p  y 
#
#
#       Last update: IH240717
#
#
"""
Demo application to run on the Raspberry Pi MRSM controller:  Display presentation
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

from PyQt6.QtWidgets import         \
    QApplication,                   \
    QWidget,                        \
    QGridLayout,                    \
    QPushButton


from MRSM_Globals import IsWaveShareDisplayEmulated
from MRSM_Globals import IsRaspberryPi5Emulated


class MRSM_Presentation():
     
    class MRSM_PushButton(QPushButton):
        def __init_subclass__(cls) -> None:
            return super().__init_subclass__()
          

    def __init__(self):
        self.MRSM_Window = QWidget()

        #   This implementation targets the 
        #   https://www.waveshare.com/11.9inch-HDMI-LCD.htm
        #   display.
        #   Resolution 320 x 1480

        if IsWaveShareDisplayEmulated:
            self.MRSM_Window.setGeometry(100,200,1480,320)

        # see https://doc.qt.io/qtforpython-6/overviews/stylesheet-examples.html
        self.MRSM_Window.setStyleSheet("QPushButton { background-color: yellow }")

        grid = QGridLayout()
        self.MRSM_Window.setLayout(grid)
     
        #IH240717 for debugging only
        b1 = self.MRSM_PushButton("QUIT",self.MRSM_Window)
        b1.clicked.connect(self.quit_clicked)
        grid.addWidget(b1,0,0)
        
        #IH240717 for debugging only
        b2 = self.MRSM_PushButton("QUIT",self.MRSM_Window)
        b2.clicked.connect(self.quit_clicked)
        grid.addWidget(b2,1,1)

        #IH240717 for debugging only
        b3 = self.MRSM_PushButton("QUIT",self.MRSM_Window)
        b3.clicked.connect(self.quit_clicked)
        grid.addWidget(b3,2,2)

    def quit_clicked(self):
        """
        TODO implement fully
        """
        QApplication.quit()
     
    def show(self):
        if IsWaveShareDisplayEmulated:
            self.MRSM_Window.show()
        else:
            self.MRSM_Window.showFullScreen()