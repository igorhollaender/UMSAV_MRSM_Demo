#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  C  o  n  t  r  o  l  l  e  r  .  p  y 
#
#
__version__ = "IH240715a"
#
#
"""
Demo application to run on the Raspberry Pi MRSM controller:  
Controller of the Raspberry Pi hardware
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

class MRSM_Controller():

     def __init__(self):
        error_message(message = "This is CamScan, Version " + __version__)

        self.camPort = camport 
        self.currentImage = None
        self.currentResult = 0
                                                       # for Microsoft Lifecam Studio HD
        self.actualFocusValue = args.focus             # IH230310 I found this to be in the range 0 (far) to 40 (near)
        self.actualExposureValue = args.exposure       # IH230310 I found this to be in the range -16 (dark) to 0 (bright)

        self.selectedROI = None

        self.GetCameraMaxResolution()
        # for the Microsoft lifecam studi

