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
#       Last update: IH240719
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
from typing import Any

from PyQt6.QtCore import (
    QUrl,
    QTimer,
    Qt
)

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QPushButton,
    QLabel
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
             
        def localizeShortString(self,sourceEnTerm: str):
            if self.targetLanguage==Language.ENGLISH:
                return sourceEnTerm
            l = list(map(lambda dictRecord: self.getTgtTerm(sourceEnTerm,dictRecord), self.d))
            # Get first non None value from List
            return next((elem for elem in l if elem is not None), sourceEnTerm)  #IH240719 if the term is not found in the dictionary, the english term is returned

    
    def __init__(self,tgtLanguage: Language) -> None:
        """
        """
        self.dictionary = self.MRSM_Dictionary(tgtLanguage)
    
    def localizeShortString(self,sourceEnTerm: str):
        return self.dictionary.localizeShortString(sourceEnTerm)
    
    def localizeLongString(self,sourceEnStringID: int):
        #IH240729 TODO implement
        return "NOT IMPLEMENTED"
    
    def UNITTEST(self):
        self.targetLangauge = Language.SLOVAK
        print(
            self.localizeShortString('QUIT'),
            self.localizeShortString('STOP'),
            self.localizeShortString('stop'),
            self.localizeShortString('FINISH'),
            self.localizeShortString('NONSEnse'),
        )
        self.targetLangauge = Language.GERMAN
        print(
            self.localizeShortString('QUIT'),
            self.localizeShortString('STOP'),
            self.localizeShortString('stop'),
            self.localizeShortString('FINISH'),
            self.localizeShortString('NONSEnse'),
        )

class MRSM_Presentation():
             
    class MRSM_PushButton(QPushButton):
    # TODO IH240718 implement inherent label localization
        def __init_subclass__(cls) -> None:
            return super().__init_subclass__()
    
    class MRSM_VideoWidget(QVideoWidget):
        def __init__(self, parent: QWidget | None = ...) -> None:
            super().__init__(parent)

    class ShowIntro():
        """
        The app starts with this scenario. If the user does not click 'QUIT'
        within the INTRO_DURATION timeslot, the app continues with ShowMain, otherwise
        it exits to OS. 
        """
        
        INTRO_DURATION_SEC  = 5

        def __init__(self,parent) -> None:

            self.grid = parent.grid
            self.parent = parent
            self.remaining_time_s = self.INTRO_DURATION_SEC

            self.l1 = QLabel(f"{parent.lcll(101)} {self.remaining_time_s} s")
            self.grid.addWidget(self.l1,1,2)

            self.b1 = parent.MRSM_PushButton(parent.lcls('QUIT'),parent.MRSM_Window)
            self.b1.clicked.connect(self.parent.quit_clicked)
            self.grid.addWidget(self.b1,2,2)

            self.timer = QTimer()
            self.timer.timeout.connect(self.on_timeout)

        def on_timeout(self):

            self.parent.quit_intro_start_main()
        
        def activate(self):
            self.l1.show()
            self.b1.show()
            self.timer.start(self.INTRO_DURATION_SEC*1000)
    

        def deactivate(self):
            self.l1.hide()
            self.b1.hide()
            pass
    
    class ShowMain():
        
        def __init__(self,parent) -> None:
            
            self.grid = parent.grid

            #videoplayer test
            self.media_player = QMediaPlayer()
            self.media_player.setSource(QUrl.fromLocalFile("resources/video/BAMBU1.mp4"))
            self.video_widget = QVideoWidget()
            self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            self.media_player.setVideoOutput(self.video_widget)
            self.media_player.setLoops(1000)
                #IH240718 should be set to Infinite, but I do not know where to find the constant
                # QMediaPlayer.Infinite is not defined
            self.grid.addWidget(self.video_widget,0,0,3,2)
        
            #IH240717 for debugging only
            self.b1 = parent.MRSM_PushButton(parent.lcls('QUIT'),parent.MRSM_Window)
            self.b1.clicked.connect(parent.quit_clicked)
            self.grid.addWidget(self.b1,0,2)
            
            #IH240717 for debugging only
            self.b2 = parent.MRSM_PushButton(parent.lcls('STOP'),parent.MRSM_Window)
            self.b2.clicked.connect(parent.quit_clicked)
            self.grid.addWidget(self.b2,1,2)

            #IH240717 for debugging only
            self.b3 = parent.MRSM_PushButton(parent.lcls('FINISH'),parent.MRSM_Window)
            self.b3.clicked.connect(parent.quit_clicked)
            self.grid.addWidget(self.b3,2,2)

            self.deactivate()
            
        def activate(self):
            self.b1.show()
            self.b2.show()
            self.b3.show()
            self.video_widget.show()
            
            self.media_player.play()
            

        def deactivate(self):
            self.b1.hide()
            self.b2.hide()
            self.b3.hide()
            self.video_widget.hide()
            
            self.media_player.stop()
            

    def lcls(self,s):
        return self.localizer.localizeShortString(s)
    
    def lcll(self,id):
        return self.localizer.localizeLongString(id)
    
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

        self.grid = QGridLayout()
        self.MRSM_Window.setLayout(self.grid)

        self.showIntro = self.ShowIntro(self)
        self.showMain = self.ShowMain(self)

        self.showIntro.activate()
        # self.showMain.activate()
        
    def quit_intro_start_main(self):
        self.showIntro.deactivate()
        self.showMain.activate()

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