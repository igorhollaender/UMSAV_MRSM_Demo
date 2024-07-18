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
#       Last update: IH240718
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

from enum import Enum

from PyQt6.QtCore import (
    QUrl,
    Qt
)

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton
)                  
    
from PyQt6.QtMultimedia import (
    QMediaPlayer,
    QAudioOutput
)

from PyQt6.QtMultimediaWidgets import \
    QVideoWidget

from MRSM_Globals import IsWaveShareDisplayEmulated
from MRSM_Globals import IsRaspberryPi5Emulated

from MRSM_Stylesheet import MRSM_Stylesheet

class Language(Enum):
        ENGLISH         = 0
        SLOVAK          = 1
        GERMAN          = 2

class PoorMansLocalizer():
    """
    Primitive localizer: translates the source English terms and phrases used in GUI
    to target language

    TODO:  implement translation for longer text portions
    """    
    
    class MRSM_Dictionary():
        """
        ENGLISH to (targetLanguage) TRANSLATIONS
        """
        d = [
            {   'enSrcTerm': 'QUIT',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'OPUSTIŤ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'VERLASSEN'},
            ]},
            {   'enSrcTerm': 'STOP',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'ZASTAVIŤ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'STEHENBLEIBEN'},
            ]},
            {   'enSrcTerm': 'FINISH',
                'trsl': [{'tgtLng':  Language.SLOVAK,  'tgtTerm': 'SKONČIŤ'},
                         {'tgtLng':  Language.GERMAN,  'tgtTerm': 'FERTIGMACHEN'},
            ]},
        ]

        def __init__(self,targetLanguage: Language) -> None:
            """
            Current options for target language include:
                SLOVAK
                GERMAN (not fully implemented)
            """
            self.targetLanguage = targetLanguage
        
        def getTgtTerm(self,srcTerm: str, dictRecord: dict) -> str:
            if dictRecord['enSrcTerm'] == srcTerm.upper():
                for langRecord in dictRecord['trsl']:
                    if langRecord['tgtLng'] == self.targetLanguage:
                        return langRecord['tgtTerm']
                return None
            else:
                return None
             
        def localizeString(self,sourceEnTerm: str):
            if self.targetLanguage==Language.ENGLISH:
                return sourceEnTerm
            l = list(map(lambda dictRecord: self.getTgtTerm(sourceEnTerm,dictRecord), self.d))
            # Get first non None value from List
            return next((elem for elem in l if elem is not None), None)

    
    def __init__(self,tgtLanguage: Language) -> None:
        """
        """
        self.dictionary = self.MRSM_Dictionary(tgtLanguage)
    
    def localizeString(self,sourceEnTerm: str):
        return self.dictionary.localizeString(sourceEnTerm)
    
    def UNITTEST(self):
        self.targetLangauge = Language.SLOVAK
        print(
            self.localizeString('QUIT'),
            self.localizeString('STOP'),
            self.localizeString('stop'),
            self.localizeString('FINISH'),
            self.localizeString('NONSEnse'),
        )
        self.targetLangauge = Language.GERMAN
        print(
            self.localizeString('QUIT'),
            self.localizeString('STOP'),
            self.localizeString('stop'),
            self.localizeString('FINISH'),
            self.localizeString('NONSEnse'),
        )

class MRSM_Presentation():
             
    class MRSM_PushButton(QPushButton):
    # TODO IH240718 implement inherent label localization
        def __init_subclass__(cls) -> None:
            return super().__init_subclass__()
    
    class MRSM_VideoWidget(QVideoWidget):
        def __init__(self, parent: QWidget | None = ...) -> None:
            super().__init__(parent)

    def lcl(self,s):
        return self.localizer.localizeString(s)
    
    def __init__(self,
            language=Language.ENGLISH
            ):
        self.language = language
        self.MRSM_Window = QWidget()

        #   This implementation targets the 
        #   https://www.waveshare.com/11.9inch-HDMI-LCD.htm
        #   display.
        #   Resolution 320 x 1480

        if IsWaveShareDisplayEmulated:
            self.MRSM_Window.setGeometry(100,200,1480,320)


        self.localizer = PoorMansLocalizer(self.language)
        #IH240717 for debugging only
        # self.localizer.UNITTEST()
        

        # see https://doc.qt.io/qtforpython-6/overviews/stylesheet-examples.html
        # self.MRSM_Window.setStyleSheet("QPushButton { background-color: yellow }")
        self.MRSM_Window.setStyleSheet(MRSM_Stylesheet())

        grid = QGridLayout()
        self.MRSM_Window.setLayout(grid)

        
        #videoplayer test
        self.media_player = QMediaPlayer()
        self.media_player.setSource(QUrl.fromLocalFile("resources/video/BAMBU1.mp4"))
        self.video_widget = QVideoWidget()
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setLoops(1000)
            #IH240718 should be set to Infinite, but I do not know where to find the constant
            # QMediaPlayer.Infinite is not defined
        grid.addWidget(self.video_widget,0,0,3,2)
     
        #IH240717 for debugging only
        b1 = self.MRSM_PushButton(self.lcl('QUIT'),self.MRSM_Window)
        b1.clicked.connect(self.quit_clicked)
        grid.addWidget(b1,0,2)
        
        #IH240717 for debugging only
        b2 = self.MRSM_PushButton(self.lcl('STOP'),self.MRSM_Window)
        b2.clicked.connect(self.quit_clicked)
        grid.addWidget(b2,1,2)

        #IH240717 for debugging only
        b3 = self.MRSM_PushButton(self.lcl('FINISH'),self.MRSM_Window)
        b3.clicked.connect(self.quit_clicked)
        grid.addWidget(b3,2,2)

        self.media_player.play()


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