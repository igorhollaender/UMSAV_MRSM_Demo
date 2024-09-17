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
#       Last update: IH240917
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
#       IH240722
#       I had problems with PyQt6.QtMultimedia not found/ This DID NOT HELP
#           sudo apt-get install libqt5multimedia5-plugins qml-module-qtmultimedia
#       see 
#           https://stackoverflow.com/questions/58042974/module-qtmultimedia-is-not-installed
#


# TODOs
#-------------------------------------------------------------------------------
#
#   IH240813    moving scroll bar in INFO window has to reset the idle timer

# BUGs
#
#   IH2407151 XXX
#
#-------------------------------------------------------------------------------


from MRSM_Globals import (
    IsWaveShareDisplayEmulated,
    IsRaspberryPi5Emulated,
    IsQtMultimediaAvailable,
    HasToShowExitButton,
    HasToShowGoIdleButton,
    HasToIncludeSegmentationPanel,
)

from MRSM_Globals import __version__

from MRSM_Utilities import error_message, debug_message


from PyQt6.QtGui import (
    QColor,
    QFont,
    QPixmap,
    QPolygonF,
    QTransform,
)
from enum import Enum
from functools import partial
from typing import Any

from PyQt6.QtCore import (    
    Qt,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSequentialAnimationGroup,
    QTimer,
    QUrl
)

from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget        
)                  

if IsQtMultimediaAvailable:    
    from PyQt6.QtMultimedia import (
        QMediaPlayer,
        QAudioOutput
        )

    from PyQt6.QtMultimediaWidgets import \
        QVideoWidget


from MRSM_Controller import MRSM_Controller
from MRSM_ImageBase import ImageBase, Organ, ImagingPlane
from MRSM_Stylesheet import MRSM_Stylesheet
from MRSM_TextContent import Language, MRSM_Texts



class PoorMansLocalizer():
    """
    Primitive localizer: translates the source English terms and phrases used in GUI
    to target language
    """    
    
    class MRSM_Dictionary():
        """
        ENGLISH to (targetLanguage) TRANSLATIONS
        """
        
        def __init__(self,targetLanguage: Language) -> None:
            """
            Current options for target language include:
                SLOVAK
                ENGLISH
                GERMAN
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
            # if self.targetLanguage==Language.ENGLISH:
            #     return sourceEnTerm
            l = list(map(lambda dictRecord: self.getTgtTerm(sourceEnTerm,dictRecord), MRSM_Texts))
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
        debug_message(
            self.localizeShortString('QUIT'),
            self.localizeShortString('STOP'),
            self.localizeShortString('stop'),
            self.localizeShortString('FINISH'),
            self.localizeShortString('NONSEnse'),
            self.localizeShortString('#101'),
        )
        self.targetLangauge = Language.GERMAN
        debug_message(
            self.localizeShortString('QUIT'),
            self.localizeShortString('STOP'),
            self.localizeShortString('stop'),
            self.localizeShortString('FINISH'),
            self.localizeShortString('NONSEnse'),
            self.localizeShortString('#101'),
        )

class MRSM_Presentation():
             
    class MRSM_PushButton(QPushButton):
    # TODO IH240718 implement inherent label localization
        def __init_subclass__(cls) -> None:
            return super().__init_subclass__()
    
    if IsQtMultimediaAvailable:
        class MRSM_VideoWidget(QVideoWidget):
            def __init__(self, parent: QWidget | None = ...) -> None:
                super().__init__(parent)

    class ShowIntro():
        """
        The app starts with this scenario. If the user does not click 'QUIT'
        within the INTRO_DURATION timeslot, the app continues with ShowMain, otherwise
        it exits to OS. 
        """
        
        # IH240722 TODO: set this to 5 secs for real app
        INTRO_DURATION_SEC  = 1  
        INTRO_MESSAGE_UPDATE_INTERVAL_SEC  = 1

        def __init__(self,parent) -> None:

            self.grid = parent.grid
            self.parent = parent
            self.remaining_time_s = self.INTRO_DURATION_SEC

            self.introWidgets = []

            self.lTitle = QLabel("Magnetic Resonance Scanner Mockup")
            self.grid.addWidget(self.lTitle,0,2,4,30)
            self.lTitle.setObjectName("lTitle")  # this is for stylesheet reference 
            self.introWidgets += [self.lTitle]

            self.lVersion = QLabel(__version__)
            self.grid.addWidget(self.lVersion,4,2)
            self.lVersion.setObjectName("lVersion")  
            self.introWidgets += [self.lVersion]

            self.lCountdown = QLabel(self.composeTimeoutMessageText())
            self.grid.addWidget(self.lCountdown,4,22,1,4)
            self.lCountdown.setObjectName("lCountdown")  
            self.introWidgets += [self.lCountdown]

            self.bQuitApp = parent.MRSM_PushButton(parent.lcls('QUIT'),parent.MRSM_Window)
            self.bQuitApp.clicked.connect(self.parent.quit_app)
            self.grid.addWidget(self.bQuitApp,4,28,1,4)
            self.introWidgets += [self.bQuitApp]


            self.timer = QTimer()
            self.timer.timeout.connect(self.on_timeout)

        def composeTimeoutMessageText(self):
            return f"{self.parent.lcls('#101')} {self.remaining_time_s} {self.parent.lcls('#102')}"
            
        def on_timeout(self):
            self.remaining_time_s = self.remaining_time_s - 1
            if self.remaining_time_s <= 0:
                self.parent.quit_intro_start_main()
            else:
                self.lCountdown.setText(self.composeTimeoutMessageText())
                self.timer.start(self.INTRO_MESSAGE_UPDATE_INTERVAL_SEC*1000)
        
        def activate(self):
            for w in self.introWidgets:
                w.show()
            self.remaining_time_s = self.INTRO_DURATION_SEC
            self.timer.start(self.INTRO_MESSAGE_UPDATE_INTERVAL_SEC*1000)
    
        def deactivate(self):
            for w in self.introWidgets:
                w.hide()            
            self.timer.stop()
    
    class ShowMain():

        class RollShade(QLabel):
            def __init_subclass__(cls) -> None:
                super().__init_subclass__()
            #IH240724 implement
                
        class OrganButton(QGraphicsItem):   

            def __init__(self, x, y, width, height, showMainInstance):
                super().__init__()
                self.rect = QRectF(x, y, width, height)                
                self.setAcceptHoverEvents(True)
                self.setAcceptTouchEvents(True)
                self.isMousePressed = False
                self.showMainInstance = showMainInstance
                self.brushActive            = Qt.GlobalColor.green
                self.penActive              = Qt.GlobalColor.green
                self.brushIdle              = Qt.GlobalColor.yellow
                self.brushRunningShown      = Qt.GlobalColor.red
                self.brushIdleShown         = Qt.GlobalColor.green
                self.brushIdleNotShown      = Qt.GlobalColor.yellow
                self.penIdle = Qt.GlobalColor.yellow
                # self.setActiveState(False)
                self.setCurrentState(isScanningRunning=False,isCurrentlyShown=False)

            def boundingRect(self):
                return self.rect
            
            #IH240822 OBSOLETE (use setCurrentState instead)
            def setActiveState(self, active : bool = False):                
                self.myBrush = self.brushActive if active else self.brushIdle    	        
                self.myPen = self.penActive if active else self.penIdle

            def setCurrentState(self, isScanningRunning: bool = False, isCurrentlyShown: bool = False):                             
                self.myBrush = self.brushRunningShown   if      isScanningRunning   and     isCurrentlyShown else (                    
                               self.brushIdleShown      if not  isScanningRunning   and     isCurrentlyShown else (
                               self.brushIdleNotShown   if not  isScanningRunning   and not isCurrentlyShown else self.brushIdle))

                self.myPen = self.penActive if isScanningRunning else self.penIdle

              
            def paint(self, painter, option, widget):
                #IH240724 PROBLEM this does not work as expected
                #if self.isMousePressed:
                #    painter.setPen(Qt.GlobalColor.red)
                #    painter.setBrush(Qt.GlobalColor.red)
                #else:
                #    painter.setPen(Qt.GlobalColor.yellow)
                #    painter.setBrush(Qt.GlobalColor.yellow)
                painter.setPen(self.myPen)
                painter.setBrush(self.myBrush)
                painter.setOpacity(0.5)
                painter.drawEllipse(self.rect)

            def mousePressEvent(self, event):                
                self.isMousePressed = True
                # debug_message(f"selected organ: {self.data(1)}")
                self.ScanOrgan(self.data(1))
                self.update()
                super().mousePressEvent(event)
            
            def mouseReleaseEvent(self, event):                
                self.isMousePressed = False
                self.update()
                super().mouseReleaseEvent(event)

            def hoverEnterEvent(self, event):
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                super().hoverEnterEvent(event)

            def hoverLeaveEvent(self, event):
                self.setCursor(Qt.CursorShape.ArrowCursor)
                super().hoverLeaveEvent(event)
        
            def ScanOrgan(self,organ: Organ ):
                self.showMainInstance.presentMRScanning(organ)

        def __init__(self,parent) -> None:
            
            self.parent : QWidget       = parent
            self.grid   : QGridLayout   = parent.grid 
            self.mainWidgets = []

            #videoplayer test only
            if IsQtMultimediaAvailable:    
                #IH240722 PROBLEM cannot load PyQt6.QtMultimedia for RPI        
                self.media_player = QMediaPlayer()
                self.media_player.setSource(QUrl.fromLocalFile("resources/video/BAMBU1.mp4"))
                self.video_widget = QVideoWidget()
                self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatioByExpanding)
                self.media_player.setVideoOutput(self.video_widget)
                self.media_player.setLoops(1000)
                    #IH240718 should be set to Infinite, but I do not know where to find the constant
                    # QMediaPlayer.Infinite is not defined
                self.grid.addWidget(self.video_widget,0,0,3,2)
                
            self.bInfo = self.parent.MRSM_PushButton(self.parent.lcls('INFO'),self.parent.MRSM_Window)
            self.bInfo.clicked.connect(self.parent.quit_main_start_info)
            self.grid.addWidget(self.bInfo,0,22,1,10)
            self.mainWidgets += [self.bInfo]

            
            self.bDescription = self.parent.MRSM_PushButton(self.parent.lcls('WHAT UC'),self.parent.MRSM_Window)
            self.bDescription.clicked.connect(self.parent.quit_main_start_description)
            if HasToIncludeSegmentationPanel:            
                self.grid.addWidget(self.bDescription,1,22,1,10)
                self.mainWidgets += [self.bDescription]
            else:
                self.bDescription.hide()

            #IH240717 for debugging only
            if HasToShowExitButton:
                self.b1 = self.parent.MRSM_PushButton(self.parent.lcls('QUIT'),self.parent.MRSM_Window)
                self.b1.clicked.connect(self.parent.quit_app)
                self.grid.addWidget(self.b1,2,22,1,10)
                self.mainWidgets += [self.b1]
            
            #IH240720 for debugging only
            # self.b2 = self.parent.MRSM_PushButton(self.parent.lcls('LED ON'),self.parent.MRSM_Window)
            # self.b2.clicked.connect(self.parent.ledon)
            # self.grid.addWidget(self.b2,2,22,1,20)
            # self.mainWidgets += [self.b2]

            
            #IH240717 for debugging only
            # self.b4 = self.parent.MRSM_PushButton(self.parent.lcls('START VIDEO'),self.parent.MRSM_Window)
            # self.b4.clicked.connect(self.video_start)
            # self.grid.addWidget(self.b4,3,22,1,10)

            #IH240717 for debugging only
            if HasToShowGoIdleButton:
                self.b3 = self.parent.MRSM_PushButton(self.parent.lcls('GO IDLE'),self.parent.MRSM_Window)
                self.b3.clicked.connect(self.parent.quit_main_start_idle)
                self.grid.addWidget(self.b3,3,22,1,10)
                self.mainWidgets += [self.b3]

            self.pixmapPatient = QPixmap("resources/images/diverse/MRSM_patient_240722.jpg")
            self.pixmapPatientScaled = self.pixmapPatient.scaled(800,220,  #IH240723 do not change this!!: 800,200
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            
            QLabelAsPixmapContainer = False
            QGraphicsSceneAsPixmapContainer = True
            if QLabelAsPixmapContainer:
                self.imagePaneRightmost  = QLabel("",self.parent.MRSM_Window)    
                self.imagePaneRightmost.setPixmap(self.pixmapPatientScaled)     
                self.imagePaneRightmost.setStyleSheet("background-color: green")
            if QGraphicsSceneAsPixmapContainer:
                self.patientScene  = QGraphicsScene(self.parent.MRSM_Window)                                  
                self.pixmapPatientScaled = self.pixmapPatient.scaled(700,220,  #IH240917 700,220 was OK
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                self.patientPixmapOnScene = self.patientScene.addPixmap(self.pixmapPatientScaled)                 
                 
                f = QFont()
                f.setPointSize(15)
                f.setBold(True)                
                self.patientScene.addText(parent.lcls("#105"),font=f).setPos(10,-50)

                #IH240917 HACK covering a unpleasant bar under the patient image with a rectangle
                self.patientScene.addRect(0,223,472,27,brush=Qt.GlobalColor.darkCyan,pen=Qt.GlobalColor.transparent)
                
             
                # organ graphics buttons
                #  
                self.organButton = dict()
                 
        
                self.organButton[Organ.KNEE] = self.OrganButton(120,100,40,40,self)
                self.organButton[Organ.KNEE].setData(1,Organ.KNEE)
                self.patientScene.addItem(self.organButton[Organ.KNEE])

                self.organButton[Organ.HEAD] = self.OrganButton(410,40,40,40,self)
                self.organButton[Organ.HEAD].setData(1,Organ.HEAD)
                self.patientScene.addItem(self.organButton[Organ.HEAD])

                self.organButton[Organ.HAND] = self.OrganButton(220,135,40,40,self)
                self.organButton[Organ.HAND].setData(1,Organ.HAND)
                self.patientScene.addItem(self.organButton[Organ.HAND])

                self.organButton[Organ.BODY] = self.OrganButton(280,70,40,40,self)
                self.organButton[Organ.BODY].setData(1,Organ.BODY)
                self.patientScene.addItem(self.organButton[Organ.BODY])

                self.imagePaneRightmost = QGraphicsView(self.patientScene)


            self.grid.addWidget(self.imagePaneRightmost, 0,12,5,10)              
            self.imagePanels = [self.imagePaneRightmost]
            self.imagePaneRightmost.setObjectName("imagePaneRightmost")

            self.imagePaneLeft  = QLabel("",self.parent.MRSM_Window)
            self.imagePaneMid   = QLabel("",self.parent.MRSM_Window)
            self.imagePaneRight = QLabel("",self.parent.MRSM_Window)
            self.imagePanelsMRI = [self.imagePaneLeft,self.imagePaneMid,self.imagePaneRight]
            self.imagePanels += self.imagePanelsMRI
            self.mainWidgets += self.imagePanels

            self.lRollerShadePaneLeft = QLabel("",self.imagePaneLeft)
            self.lRollerShadePaneLeft.setFixedHeight(320)
            self.lRollerShadePaneLeft.setObjectName("lRollerShadePaneLeft")
            self.lRollerShadePaneMid = QLabel("",self.imagePaneMid)
            self.lRollerShadePaneMid.setFixedHeight(320)
            self.lRollerShadePaneMid.setObjectName("lRollerShadePaneMid")
            self.lRollerShadePaneRight = QLabel("",self.imagePaneRight)
            self.lRollerShadePaneRight.setFixedHeight(320)
            self.lRollerShadePaneRight.setObjectName("lRollerShadePaneRight")

            
            self.grid.addWidget(self.imagePaneLeft, 0,0,4,4)
            self.grid.addWidget(self.imagePaneMid,  0,4,4,4)
            self.grid.addWidget(self.imagePaneRight,  0,8,4,4)

            self.grid.addWidget(self.lRollerShadePaneLeft, 0,0,5,4,alignment=Qt.AlignmentFlag.AlignBottom)
            self.grid.addWidget(self.lRollerShadePaneMid, 0,4,5,4,alignment=Qt.AlignmentFlag.AlignBottom)
            self.grid.addWidget(self.lRollerShadePaneRight, 0,8,5,4,alignment=Qt.AlignmentFlag.AlignBottom)

            self.mainWidgets += [self.lRollerShadePaneLeft,
                                 self.lRollerShadePaneMid,
                                 self.lRollerShadePaneRight]
            
            self.pixmapStandardSize = 290
            

            for panel in self.imagePanelsMRI:
                panel.setMinimumHeight(self.pixmapStandardSize)
                panel.setMaximumHeight(self.pixmapStandardSize)
                panel.setMinimumWidth(self.pixmapStandardSize)
                panel.setMaximumWidth(self.pixmapStandardSize)

                panel.setScaledContents(True)

            # animation setup
            self.animation_rollerLeft = QPropertyAnimation(self.lRollerShadePaneLeft,b"pos")
            self.animation_rollerMid  = QPropertyAnimation(self.lRollerShadePaneMid,b"pos")
            self.animation_rollerRight= QPropertyAnimation(self.lRollerShadePaneRight,b"pos")

            ROLLING_DURATION_MSEC = 2000

            self.animation_rollerLeft.setDuration(ROLLING_DURATION_MSEC)
            self.animation_rollerLeft.setStartValue(QPoint(11,-10))
            self.animation_rollerLeft.setEndValue(QPoint(11,320))

            #IH240725 this does not work, since at this moment, the x is 0 (and not 11)
            #IH240725 TODO implement correctly
            # debug_message(self.imagePaneLeft.geometry().x())
            # self.animation_rollerLeft.setStartValue(QPoint(self.imagePaneLeft.geometry().x(),-10))
            # self.animation_rollerLeft.setEndValue(QPoint(self.imagePaneLeft.geometry().x(),self.imagePaneLeft.geometry().height()+30))
            
            self.animation_rollerMid.setDuration(ROLLING_DURATION_MSEC)
            self.animation_rollerMid.setStartValue(QPoint(307,-10))
            self.animation_rollerMid.setEndValue(QPoint(307,320))

            self.animation_rollerRight.setDuration(ROLLING_DURATION_MSEC)
            self.animation_rollerRight.setStartValue(QPoint(603,-10))
            self.animation_rollerRight.setEndValue(QPoint(603,320))

            self.animation_all = QSequentialAnimationGroup()
            self.animation_all.addAnimation(self.animation_rollerLeft)
            self.animation_all.addAnimation(self.animation_rollerMid)
            self.animation_all.addAnimation(self.animation_rollerRight)
            self.animation_all.finished.connect(self.on_animation_finished)
            
            self.isSimulationShowRunning = False
            self.presentMRScanning(Organ.NONE)
            self.deactivate()

        
        def setRollerShadesToInitialPosition(self):
            """
            Initial position is 'fully shading/covering the images'
            """
            # debug_message(self.imagePaneLeft.geometry())
            # debug_message(self.imagePaneMid.geometry())
            # debug_message(self.imagePaneRight.geometry())

            self.lRollerShadePaneLeft.show()
            self.lRollerShadePaneLeft.setGeometry(self.imagePaneLeft.geometry())
            self.lRollerShadePaneLeft.y = self.imagePaneLeft.geometry().y()-20
            self.lRollerShadePaneMid.show()
            self.lRollerShadePaneMid.setGeometry(self.imagePaneMid.geometry())
            self.lRollerShadePaneMid.y = self.imagePaneMid.geometry().y()-20
            self.lRollerShadePaneRight.show()
            self.lRollerShadePaneRight.setGeometry(self.imagePaneRight.geometry())
            self.lRollerShadePaneRight.y = self.imagePaneRight.geometry().y()-20
            
        def activate(self) -> None:
            self.reactivate()
            self.setRollerShadesToInitialPosition()
            self.isSimulationShowRunning = False
            for o in self.organButton.keys(): 
                self.organButton[o].setCurrentState(isScanningRunning=False,isCurrentlyShown=False)
            self.imagePaneRightmost.update()
            self.bDescription.setEnabled(False)

        def reactivate(self) -> None:
            """
            reactivation with state before deactivation restored
            """
            for panel in self.mainWidgets:
                panel.show()

            #IH240909 HACK the shade panes should actually be in 'open' state 
            self.lRollerShadePaneLeft.hide()
            self.lRollerShadePaneMid.hide()
            self.lRollerShadePaneRight.hide()        

            if IsQtMultimediaAvailable:
                self.video_widget.show()
                self.media_player.play()
            self.reset_idle_timer()
            if not IsWaveShareDisplayEmulated:
                self.parent.ShowFullScreen()
            
        def deactivate(self) -> None:
            for panel in self.mainWidgets:
                panel.hide()
            self.animation_all.stop()

            self.isSimulationShowRunning = False

            if IsQtMultimediaAvailable:                
                self.video_widget.hide()
                self.media_player.stop()    

        def presentMRScanning(self,organ :Organ) -> None:
            """
            Scenario following pressing an organ button on the patient graphics
            """            
            if self.isSimulationShowRunning:
                return
            
            self.currentOrgan = organ
            
            for o in self.organButton.keys(): 
                # self.organButton[o].setActiveState(False)
                self.organButton[o].setCurrentState(isScanningRunning=False,isCurrentlyShown=False)
            self.imagePaneRightmost.update()            
            self.bDescription.setEnabled(False)

            if organ !=organ.NONE:
                self.setRollerShadesToInitialPosition()
                
                # clean all pixmaps
                self.imagePaneLeft.setPixmap(QPixmap())
                self.imagePaneMid.setPixmap(QPixmap())
                self.imagePaneRight.setPixmap(QPixmap())

                pm = self.parent.MRSM_ImageBase.getScaledPixmap(self.currentOrgan,ImagingPlane.SAGITTAL)
                if pm is not None:                
                    self.imagePaneLeft.setPixmap(pm)
                pm = self.parent.MRSM_ImageBase.getScaledPixmap(self.currentOrgan,ImagingPlane.CORONAL)
                if pm is not None:                
                    self.imagePaneMid.setPixmap(pm)
                pm = self.parent.MRSM_ImageBase.getScaledPixmap(self.currentOrgan,ImagingPlane.TRANSVERSAL)
                if pm is not None:                
                    self.imagePaneRight.setPixmap(pm)                    
                

                self.isSimulationShowRunning = True
                self.organButton[self.currentOrgan].setCurrentState(isScanningRunning=True,isCurrentlyShown=True)
                self.imagePaneRightmost.update()
                self.parent.hardwareController.scanningSimulationShowStart(organ=self.currentOrgan,imagingPlane=ImagingPlane.ARBITRARY)                
                self.animation_all.start()
                self.parent.idle_timer.stop()   #IH240812 avoid going idle during animation

                                


        def on_animation_finished(self):
            debug_message('animation finished')
            self.isSimulationShowRunning = False
            # self.organButton[self.currentOrgan].setActiveState(False)
            self.organButton[self.currentOrgan].setCurrentState(isScanningRunning=False,isCurrentlyShown=True)
            self.parent.hardwareController.scanningSimulationShowStop()
            self.imagePaneRightmost.update()

            #IH240909 added
            self.bDescription.setEnabled(True)
                
            self.reset_idle_timer()
            
        #IH240724 OBSOLETE
        def video_start(self):
            if IsQtMultimediaAvailable:                
                self.media_player.play()
            self.reset_idle_timer()

        #IH240724 OBSOLETE
        def video_stop(self):
            if IsQtMultimediaAvailable:                
                self.media_player.stop()
            self.reset_idle_timer()     
            #IH240719 TODO implement implicit adding self.reset_idle_timer()  to all user actions
    
        def reset_idle_timer(self):
            self.parent.idle_timer.stop()
            self.parent.idle_timer.start(self.parent.ShowIdle.IDLE_BREAK_DURATION_SEC*1000)
            
    class ShowIdle():
        """
        This scenario applies after a longer inactivity break (IDLE_BREAK_DURATION_SEC) of the ShowMain.
        """
        IDLE_BREAK_DURATION_SEC  = 30  # IH240729 set to 30 for real app

        def __init__(self,parent) -> None:

            self.grid :   QGridLayout   = parent.grid
            self.parent : QWidget       = parent
            self.idleWidgets = []

            self.bgLabel = QLabel("",self.parent.MRSM_Window)
            self.grid.addWidget(self.bgLabel,0,0,4,32)  #IH240723 do not change this!
            self.bgPixmap = QPixmap("resources/images/diverse/MRSM_fullview_240722.jpg")            
            self.bgLabel.setPixmap(self.bgPixmap.scaled(1480,320,Qt.AspectRatioMode.KeepAspectRatioByExpanding))
            
            #IH240729 This is necessary to prevent the image from voluntarily resizing
            self.bgLabel.setMinimumHeight(300)            
            self.bgLabel.setMaximumHeight(300)            
            self.bgLabel.setMinimumWidth(1460)            
            self.bgLabel.setMaximumWidth(1460)            

            self.idleWidgets += [self.bgLabel]

            self.lIdleTitleBig = QLabel(parent.lcls("#103"))
            self.grid.addWidget(self.lIdleTitleBig,1,2,1,20)
            self.lIdleTitleBig.setObjectName("lIdleTitleBig")  # this is for stylesheet reference 
            self.idleWidgets += [self.lIdleTitleBig]

            self.lIdleTitleSmall = QLabel(parent.lcls("#104"))
            self.grid.addWidget(self.lIdleTitleSmall,2,2,1,15)
            self.lIdleTitleSmall.setObjectName("lIdleTitleSmall")  # this is for stylesheet reference 
            self.idleWidgets += [self.lIdleTitleSmall]

            self.bResumeApp = parent.MRSM_PushButton('...',parent.MRSM_Window)
            self.bResumeApp.clicked.connect(self.parent.quit_idle_start_main)
            self.grid.addWidget(self.bResumeApp,2,27,1,4)
            self.idleWidgets += [self.bResumeApp]

            self.deactivate()

        def activate(self):            
            for w in self.idleWidgets:                                
                w.show()      
            self.parent.show()
    
        def deactivate(self):
            for w in self.idleWidgets:
                w.hide()

    class ShowInfo():
        """
        Info including briefing about MRI and acknowledgments for resources used
        """
        IDLE_INACTIVITY_DURATION_SEC = 30

        def __init__(self,parent) -> None:

            self.grid :   QGridLayout   = parent.grid
            self.parent : QWidget       = parent
            self.infoWidgets = []

            self.bgLabel = QLabel("",self.parent.MRSM_Window)
            self.grid.addWidget(self.bgLabel,0,0,4,32)  #IH240723 do not change this!
            
            #IH240729 This is necessary to prevent the image from voluntarily resizing
            self.bgLabel.setMinimumHeight(300)            
            self.bgLabel.setMaximumHeight(300)            
            self.bgLabel.setMinimumWidth(1460)            
            self.bgLabel.setMaximumWidth(1460)            

            self.infoWidgets += [self.bgLabel]

            self.lHTMLText1 = QLabel(parent.lcls("#106"))
            self.lHTMLText1.setWordWrap(True)
            self.lHTMLText1.setMinimumWidth(1000)
            self.lHTMLText1.setMaximumWidth(1000)

            #IH240822 for debugging only
            # self.lHTMLText1.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse) 
            
            # self.grid.addWidget(self.lHTMLText1,0,0,4,27)
            self.saHTMLText1 = QScrollArea()
            self.saHTMLText1.setWidget(self.lHTMLText1)
            self.saHTMLText1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.saHTMLText1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.grid.addWidget(self.saHTMLText1,0,0,4,28)                                    
            self.saHTMLText1.verticalScrollBar().sliderMoved.connect(self.reset_idle_timer)
            self.lHTMLText1.setObjectName("lHTMLText1")  # this is for stylesheet reference 
            
            # self.infoWidgets += [self.lHTMLText1]
            self.infoWidgets += [self.saHTMLText1]

            self.bResumeApp = parent.MRSM_PushButton(parent.lcls('BACK'),parent.MRSM_Window)
            self.bResumeApp.clicked.connect(self.parent.quit_info_start_main)
            self.grid.addWidget(self.bResumeApp,2,29,1,4)
            self.infoWidgets += [self.bResumeApp]

            self.deactivate()

        def activate(self):            
            for w in self.infoWidgets:                                
                w.show()      
            self.parent.show()
            self.reset_idle_timer()  
    
        def deactivate(self):
            for w in self.infoWidgets:
                w.hide()

        def reset_idle_timer(self):
            self.parent.idle_timer.stop()
            self.parent.idle_timer.start(self.IDLE_INACTIVITY_DURATION_SEC*1000)
    
    class ShowDescription():
        """
        Panel showing image description, typically: annotated image segmentation 
        """
        IDLE_INACTIVITY_DURATION_SEC = 30

        def __init__(self,parent) -> None:

            self.grid :   QGridLayout   = parent.grid
            self.parent : QWidget       = parent
            self.descriptionWidgets = []
            self.annotationItems = []

            self.bgLabel = QLabel("",self.parent.MRSM_Window)
            self.grid.addWidget(self.bgLabel,0,0,4,32)  #IH240723 do not change this!
            
            #IH240729 This is necessary to prevent the image from voluntarily resizing
            self.bgLabel.setMinimumHeight(300)            
            self.bgLabel.setMaximumHeight(300)            
            self.bgLabel.setMinimumWidth(1460)            
            self.bgLabel.setMaximumWidth(1460)            

            self.descriptionWidgets += [self.bgLabel]
            
            # IH240910 for initialization only
            pm = self.parent.MRSM_ImageBase.getScaledPixmap(Organ.HEAD,ImagingPlane.SAGITTAL)
            self.parent.showMain.currentOrgan = Organ.BODY

            self.imageScene = QGraphicsScene(self.parent.MRSM_Window)
            if pm is not None:                
                self.imagePixmapOnScene = self.imageScene.addPixmap(pm)
            self.imagePane = QGraphicsView(self.imageScene)
            self.grid.addWidget(self.imagePane,0,0,4,28)
            # IH240917  (0,0,4,28) is the best so far tested on RPI
            self.descriptionWidgets += [self.imagePane]
            self.imagePane.setObjectName("imagePane")

            self.bSagittal = parent.MRSM_PushButton("SAG",parent.MRSM_Window)
            self.bSagittal.setObjectName("bSagittal")  # this is for stylesheet reference 
            self.bSagittal.clicked.connect(partial(self.showAnnotationForImage,
                                                   ImagingPlane.SAGITTAL))
            self.grid.addWidget(self.bSagittal,0,29,1,4)
            self.descriptionWidgets += [self.bSagittal]

            self.bCoronal = parent.MRSM_PushButton("COR",parent.MRSM_Window)
            self.bCoronal.setObjectName("bCoronal")
            self.bCoronal.clicked.connect(partial(self.showAnnotationForImage, 
                                                  ImagingPlane.CORONAL))
            self.grid.addWidget(self.bCoronal,1,29,1,4)
            self.descriptionWidgets += [self.bCoronal]

            self.bTransversal = parent.MRSM_PushButton("TRV",parent.MRSM_Window)
            self.bTransversal.setObjectName("bTransversal")
            self.bTransversal.clicked.connect(partial(self.showAnnotationForImage,
                                                      ImagingPlane.TRANSVERSAL))
            self.grid.addWidget(self.bTransversal,2,29,1,4)
            self.descriptionWidgets += [self.bTransversal]

            self.bResumeApp = parent.MRSM_PushButton(parent.lcls('BACK'),parent.MRSM_Window)
            self.bResumeApp.clicked.connect(self.parent.quit_description_start_main)
            self.grid.addWidget(self.bResumeApp,3,29,1,4)
            self.descriptionWidgets += [self.bResumeApp]

            self.showAnnotationForImage(ImagingPlane.TRANSVERSAL) 
            #IH240916 TODO change this to TRANSVERSAL for production,
            # as SAGITTAL is missing in some organ sets

            self.deactivate()


        def showAnnotationForImage(self,imagingPlane: ImagingPlane):
        
            if imagingPlane == ImagingPlane.SAGITTAL:
                    self.setActiveRadioButton(self.bSagittal)
                    # self.lHTMLText1.setText(f"Now showing {self.parent.showMain.currentOrgan} in SAG")
            if imagingPlane == ImagingPlane.CORONAL:
                    self.setActiveRadioButton(self.bCoronal)
                    # self.lHTMLText1.setText(f"Now showing {self.parent.showMain.currentOrgan} in COR")
            if imagingPlane == ImagingPlane.TRANSVERSAL:
                    self.setActiveRadioButton(self.bTransversal)
                    # self.lHTMLText1.setText(f"Now showing {self.parent.showMain.currentOrgan} in TRV")
            
            pm = self.parent.MRSM_ImageBase.getScaledPixmap(self.parent.showMain.currentOrgan,imagingPlane)
            if pm is not None:                
                self.imagePixmapOnScene = self.imageScene.addPixmap(pm)
            self.imagePane = QGraphicsView(self.imageScene)
        
            self.annotationItems = []
            segments = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygons(
                self.parent.showMain.currentOrgan, 
                imagingPlane)
            if len(segments)>0:
                trsf = QTransform()
                trsf.scale(self.imagePixmapOnScene.boundingRect().width(),self.imagePixmapOnScene.boundingRect().height())

                for segment in segments:
                        #IH240916 TODO adapt style
                        # c o n t i n u e.  h e r e
                        segmentPure = segment[list(segment)[0]] #IH240916 HACK this is the only key
                        for subsegmentKey in segmentPure:
                            p = self.imageScene.addPolygon(trsf.map(segmentPure[subsegmentKey]),brush=QColor(255,0,0,100)) # 100 is transparency, 0 is total transparent
                            self.annotationItems += [p]
            #IH240916 for debugging only
            r1 = self.imageScene.addRect(600,200,100,20,brush=QColor(255,0,0,255))
            r2 = self.imageScene.addLine(20,20,700,210,pen=QColor(255,0,0,255))
            self.annotationItems += [r1,r2]

            
        def setActiveRadioButton(self,activeButton):
            """
            The bSagital, bCoronal, and bTransversal button work as a RadioButton group
            This methods set the active one.
            """

            #IH240909 PROBLEM here: properties cannot probably be manipulated without restoring the widget
            # so this does not work
            #for b in [self.bSagittal, self.bCoronal, self.bTransversal]:
            #    b.setProperty("activeRadioButton",None)
            #    b.setProperty("activeRadioButton",True)
            #activeButton.setProperty("activeRadioButton",None)    
            #activeButton.setProperty("activeRadioButton",True)
            # self.bSagittal.setProperty("activeRadioButton",True)  #IH240909 for debugging only

            #IH240909 HACK we simulate RadioButton behaviour by enabled/disabled mechanism
            # see also MRSM_Stylesheet.py
            for b in [self.bSagittal, self.bCoronal, self.bTransversal]:
                b.setEnabled(True)
            activeButton.setEnabled(False)  # the active button is disabled, all others are enabled
            
            

        def activate(self):            
            for w in self.descriptionWidgets:                                
                w.show()     
            #for i in self.annotationItems:                                
            #    self.imageScene.addItem(i)
            self.parent.show()
            self.showAnnotationForImage(imagingPlane=ImagingPlane.SAGITTAL)
            self.reset_idle_timer()  
    
        def deactivate(self):
            for w in self.descriptionWidgets:
                w.hide() 
            #for i in self.annotationItems:                                
            #    self.imageScene.removeItem(i)

        def reset_idle_timer(self):
            self.parent.idle_timer.stop()
            self.parent.idle_timer.start(self.IDLE_INACTIVITY_DURATION_SEC*1000)
    

    def ShowFullScreen(self):
        if IsWaveShareDisplayEmulated:
            self.MRSM_Window.show()
        else:
            self.MRSM_Window.showFullScreen()

    def lcls(self,s):
        return self.localizer.localizeShortString(s)
    
    def lcll(self,id):
        return self.localizer.localizeLongString(id)
    
    def __init__(self,
            language : Language=Language.ENGLISH,
            hardwareController : MRSM_Controller =None,
            ):
        self.language = language
        self.MRSM_Window = QWidget()
        self.hardwareController = hardwareController

        #   This implementation targets the 
        #   https://www.waveshare.com/11.9inch-HDMI-LCD.htm
        #   display.
        #   Resolution 320 x 1480

        if IsWaveShareDisplayEmulated:
            self.MRSM_Window.setGeometry(100,200,1480,320)
            self.MRSM_Window.setMinimumSize(1480,320)
            self.MRSM_Window.setMaximumSize(1480,320)


        self.localizer = PoorMansLocalizer(self.language)
        #IH240717 for debugging only
        # self.localizer.UNITTEST()
        

        # see https://doc.qt.io/qtforpython-6/overviews/stylesheet-examples.html
        # self.MRSM_Window.setStyleSheet("QPushButton { background-color: yellow }")
        self.MRSM_Window.setStyleSheet(MRSM_Stylesheet())
        self.MRSM_ImageBase = ImageBase(pixmapStandardSize=290)

        #IH240723 the standard grid layout is ...(TODO)
        self.grid = QGridLayout()
        self.MRSM_Window.setLayout(self.grid)

        self.showIntro = self.ShowIntro(self)
        self.showMain = self.ShowMain(self)
        self.showIdle = self.ShowIdle(self)
        self.showInfo = self.ShowInfo(self)
        if HasToIncludeSegmentationPanel:
            self.showDescription = self.ShowDescription(self)

        self.actual_idle_break_sec = 0

        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.on_idle_timeout)

        # IH240910 for debugging only
        self.showIntro.activate()
        # self.showDescription.activate()

    def on_idle_timeout(self):
            self.quit_main_start_idle()
            self.quit_info_start_idle()
            self.quit_description_start_idle()

    def quit_intro_start_main(self):
        self.showIntro.deactivate()
        self.showMain.activate() 

    def quit_idle_start_main(self):
        self.showIdle.deactivate()
        self.showMain.activate()

    def quit_main_start_idle(self):
        self.showMain.deactivate()
        self.showIdle.activate()

    def quit_info_start_main(self):    
        self.showInfo.deactivate()
        self.showMain.activate()
    
    def quit_main_start_info(self):
        self.showMain.deactivate()
        self.showInfo.activate()

    def quit_info_start_idle(self):    
        self.showInfo.deactivate()
        self.showIdle.activate()
    
    def quit_main_start_description(self):
        self.showMain.deactivate()
        self.showDescription.activate()

    def quit_description_start_idle(self):    
        self.showDescription.deactivate()
        self.showIdle.activate()

    def quit_description_start_main(self):    
        self.showDescription.deactivate()
        self.showMain.reactivate()  #IH240909 was 'activate' before
    

    def quit_app(self):
        """
        TODO implement fully
        """
        QApplication.quit()
     
    def show(self):
        if IsWaveShareDisplayEmulated:
            self.MRSM_Window.show()
        else:
            self.MRSM_Window.showFullScreen()
