#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#      The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  P  r  e  s  e  n  t  a  t  i  o  n  .  p  y 
#
#
#      Last update: IH241118
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
#       IH240813  DONE (?)
#         moving scroll bar in INFO window has to reset the idle timer
#   IH241001
#           the SAG,COR,TRV button on showDescription : use pictograms instead of alphabetic labels
#
# BUGs
#
#   IH2407151 XXX
#
#-------------------------------------------------------------------------------


from enum import Enum
from functools import partial, cmp_to_key
from typing import Any

from MRSM_Globals import (
    IsWaveShareDisplayEmulated,
    IsRaspberryPi5Emulated,
    IsQtMultimediaAvailable,
    IsMagneticSensorEmulated,
    HasToShowExitButton,
    HasToShowGoIdleButton,
    HasToIncludeSegmentationPanel,
)

from MRSM_Globals import __version__
from MRSM_Utilities import error_message, debug_message

from PyQt6.QtGui import (
    QColor,
    QFont,
    QPen,
    QPixmap,
    QPolygonF,
    QTransform,
)

from PyQt6.QtCore import (    
    Qt,
    QLineF,
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
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QWidget,            
)                  

if IsQtMultimediaAvailable:    
    from PyQt6.QtMultimedia import (
        QMediaPlayer,
        QAudioOutput
        )

    from PyQt6.QtMultimediaWidgets import \
        QVideoWidget


from MRSM_Controller import MRSM_Controller,MRSM_Magnetometer
from MRSM_ImageBase import ImageBase, Organ, ImagingPlane
from MRSM_Stylesheet import MRSM_Stylesheet
from MRSM_TextContent import Language, LanguageAbbrev, MRSM_Texts
# from MRSM_FieldVisualizer import FieldPlotCanvas  # IH241118 will be activated later, depending on command line parameter



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

        IH241106 the Quit button is replaced by SERVICE
        """
        
        # IH240722 TODO: set this to 5 secs for real app
        INTRO_DURATION_SEC  = 5  
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

            #IH241106 Quit replaced by Service
            # self.bQuitApp = parent.MRSM_PushButton(parent.lcls('QUIT'),parent.MRSM_Window)
            # self.bQuitApp.clicked.connect(self.parent.quit_app)
            # self.grid.addWidget(self.bQuitApp,4,28,1,4)
            # self.introWidgets += [self.bQuitApp]

            self.bRunService = parent.MRSM_PushButton(parent.lcls('SERVICE'),parent.MRSM_Window)
            self.bRunService.clicked.connect(self.parent.quit_intro_start_service)
            self.grid.addWidget(self.bRunService,4,28,1,4)
            self.introWidgets += [self.bRunService]

            #IH241113 added
            self.bRunMagnetometer = parent.MRSM_PushButton(parent.lcls('MGMETER'),parent.MRSM_Window)
            self.bRunMagnetometer.clicked.connect(self.parent.quit_intro_start_magnetometer)
            self.grid.addWidget(self.bRunMagnetometer,3,28,1,4)  #IH241113 TODO modify coordinates for RPI display
            self.introWidgets += [self.bRunMagnetometer]

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
                # self.update() #IH240930 I added this, but it does not seem to have significant effect for button response

              
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
                # self.scene().views().pop().viewport().repaint() #IH240930 I added this, but it does not seem 
                                                                  # to have significant effect for button response
                                                                  # see https://stackoverflow.com/questions/19897696/qt-force-qgraphicsitem-to-update#:~:text=According%20to%20Qt%20Documentation,%20%22%20void%20QGraphicsItem::update
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

                #IH241007 added
                self.organButton[Organ.KNEE2] = self.OrganButton(143,135,40,40,self)
                self.organButton[Organ.KNEE2].setData(1,Organ.KNEE2)
                self.patientScene.addItem(self.organButton[Organ.KNEE2])

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
                
                QApplication.processEvents() #IH240930 this is to prevent long waiting before updating the OrganButton style

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

            #IH241003 added: bDescription button is not enabled if there is nothing to show
            segmentsForSagPlane,_,_ = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygonsAndAnnotations(
                    self.parent.showMain.currentOrgan, 
                    ImagingPlane.SAGITTAL)
            segmentsForCorPlane,_,_ = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygonsAndAnnotations(
                    self.parent.showMain.currentOrgan, 
                    ImagingPlane.CORONAL)
            segmentsForTrvPlane,_,_ = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygonsAndAnnotations(
                    self.parent.showMain.currentOrgan, 
                    ImagingPlane.TRANSVERSAL)
            if len(segmentsForSagPlane)>0 or len(segmentsForCorPlane)>0 or len(segmentsForTrvPlane)>0: 
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
        IDLE_INACTIVITY_DURATION_SEC = 2*60  #IH240930 was 30 before, but this was too short for reading

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
        SEGMENT_OPACITY = 130  # from 0 to 255
            
        class LabelPositioner():

            LINEWIDTH = 3 # width of the line connecting segment and label rectangle
            TARGETDOTRADIUS = 3 # radius of the circle shown in the reference point of the segment

            def __init__(self,listOfRefPointAndLabelTuples) -> None:
                """
                typical 2nd argument is 
                    list(zip(segmentRefPoints,segmentLabels,segmentColors)
                """
                self.listOfRefPointAndLabelTuples = listOfRefPointAndLabelTuples

            def getGraphicsTupleList(self):
                
                #IH241003 reordering labels: from ref point with min y coord to max y coord
                # (this is to avoid most of the line crossings)
                listOfRefPointAndLabelTuples_Reordered = sorted(self.listOfRefPointAndLabelTuples,
                                    key=cmp_to_key(lambda tuple1,tuple2: tuple1[0].y()-tuple2[0].y()))
                                    
                graphicsTupleList =[]
                rectY = 20
                for pointAndLabelTuple in listOfRefPointAndLabelTuples_Reordered:
                 
                    P1 = QPointF(pointAndLabelTuple[0])             # reference point of the segment
                    T  = QGraphicsTextItem(pointAndLabelTuple[1])   # label text
                    P2 = QPointF(410,rectY)                         # position of the label text
                    R  = QGraphicsRectItem(400,rectY,300,25)        # label rectangle
                    
                    R.setBrush(QColor(pointAndLabelTuple[2]))               # this is the segment color, for universal use

                    graphicsTupleList += [(P1,T,P2,R)]

                    rectY += 30
                return graphicsTupleList

        def __init__(self,parent) -> None:

            self.grid :   QGridLayout   = parent.grid
            self.parent : QWidget       = parent
            self.descriptionWidgets = []
            self.segmentAndAnnotationItems = []

            self.bgLabel = QLabel("",self.parent.MRSM_Window)
            self.grid.addWidget(self.bgLabel,0,0,4,32)  #IH240723 do not change this!
            
            #IH240729 This is necessary to prevent the image from voluntarily resizing
            self.bgLabel.setMinimumHeight(300)            
            self.bgLabel.setMaximumHeight(300)            
            self.bgLabel.setMinimumWidth(1460)            
            self.bgLabel.setMaximumWidth(1460)            

            self.descriptionWidgets += [self.bgLabel]
            
            # IH240910 for initialization only
            # IH241007 OBSOLETE
            # pm = self.parent.MRSM_ImageBase.getScaledPixmap(Organ.HEAD,ImagingPlane.SAGITTAL)
            # self.parent.showMain.currentOrgan = Organ.BODY
            

            self.imageScene = QGraphicsScene(self.parent.MRSM_Window)
            # if pm is not None:                
            self.imagePixmapOnScene = self.imageScene.addPixmap(QPixmap())
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

            #I241007 OBSOLETE
            #self.showAnnotationForImage(ImagingPlane.TRANSVERSAL) 
            #IH240916 TODO change this to TRANSVERSAL for production,
            # as SAGITTAL is missing in some organ sets

            self.deactivate()


        def showAnnotationForImage(self,imagingPlane: ImagingPlane):
        
            availableImagingPlanes = {ImagingPlane.SAGITTAL,ImagingPlane.CORONAL,ImagingPlane.TRANSVERSAL}
            #IH240920 if an image is not available for the given imaging plane, hide respective button
            #IH241003 added: also hide the button if there is no segmentation available
            
            self.bSagittal.show()
            segmentsForSagPlane,_,_ = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygonsAndAnnotations(
                    self.parent.showMain.currentOrgan, 
                    ImagingPlane.SAGITTAL)
            if (self.parent.MRSM_ImageBase.getScaledPixmap(self.parent.showMain.currentOrgan,ImagingPlane.SAGITTAL) is None
                or 
                len(segmentsForSagPlane)==0
                ):
                self.bSagittal.hide()
                availableImagingPlanes.remove(ImagingPlane.SAGITTAL)
            
            self.bCoronal.show()
            segmentsForCorPlane,_,_ = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygonsAndAnnotations(
                    self.parent.showMain.currentOrgan, 
                    ImagingPlane.CORONAL)
            if (self.parent.MRSM_ImageBase.getScaledPixmap(self.parent.showMain.currentOrgan,ImagingPlane.CORONAL) is None
                or
                len(segmentsForCorPlane)==0
                ):
                self.bCoronal.hide()
                availableImagingPlanes.remove(ImagingPlane.CORONAL)
            
            self.bTransversal.show()
            segmentsForTrvPlane,_,_ = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygonsAndAnnotations(
                    self.parent.showMain.currentOrgan, 
                    ImagingPlane.TRANSVERSAL)
            if (self.parent.MRSM_ImageBase.getScaledPixmap(self.parent.showMain.currentOrgan,ImagingPlane.TRANSVERSAL) is None
                or
                len(segmentsForTrvPlane)==0
                ):
                self.bTransversal.hide()
                availableImagingPlanes.remove(ImagingPlane.TRANSVERSAL)
            
            assert len(availableImagingPlanes)>0, "No suitable imaging plane found"

            if not imagingPlane in availableImagingPlanes:
                imagingPlane = availableImagingPlanes.pop()  # HACK random selection
            if imagingPlane == ImagingPlane.SAGITTAL:
                self.setActiveRadioButton(self.bSagittal)
            if imagingPlane == ImagingPlane.CORONAL:
                self.setActiveRadioButton(self.bCoronal)
            if imagingPlane == ImagingPlane.TRANSVERSAL:
                self.setActiveRadioButton(self.bTransversal)

            pm = self.parent.MRSM_ImageBase.getScaledPixmap(self.parent.showMain.currentOrgan,imagingPlane)
            if pm is not None:                
                self.imagePixmapOnScene = self.imageScene.addPixmap(pm)
                
            for i in self.segmentAndAnnotationItems:    
                assert i is not None, "graphics item to remove is NONE"
                self.imageScene.removeItem(i)
            self.segmentAndAnnotationItems = []
            self.imagePane = QGraphicsView(self.imageScene)
        
            segments,annotations,fillColors = self.parent.MRSM_ImageBase.segmentationFactory.getSegmentQPolygonsAndAnnotations(
              self.parent.showMain.currentOrgan, 
                imagingPlane)
            
            segmentRefPoints = []
            segmentLabels = []
            segmentColors = []
            if len(segments)>0:
                trsf = QTransform()
                trsf.scale(self.imagePixmapOnScene.boundingRect().width(),self.imagePixmapOnScene.boundingRect().height())


                fillColorsIter = iter(fillColors)   #IH241002 TODO this is UGLY; needs full code/data restructuring
                for segment in segments:
                        fillColor = next(fillColorsIter)
                        segmentPure = segment[list(segment)[0]] #IH240916 HACK this is the only key
                        fillColorPure = fillColor[list(fillColor)[0]] #IH240916 HACK this is the only key
                        for subsegmentKey in segmentPure:
                             fillColorWithOpacity = QColor(fillColorPure[subsegmentKey])
                             fillColorWithOpacity.setAlpha(self.SEGMENT_OPACITY) 
                             p = self.imageScene.addPolygon(trsf.map(segmentPure[subsegmentKey]),brush=fillColorWithOpacity) 
                             p.setZValue(1)
                        self.segmentAndAnnotationItems += [p]
                        segmentRefPoints += [self.parent.MRSM_ImageBase.segmentationFactory.getSegmentReferencePoint(p)]

                for fillColor in fillColors:
                        fillColorPure = fillColor[list(fillColor)[0]] #IH240916 HACK this is the only key
                        for subsegmentKey in fillColorPure:                                       
                            segmentColors += [fillColorPure[subsegmentKey]]
                        
                for annotation in annotations:
                        annotationPure = annotation[list(annotation)[0]] #IH240916 HACK this is the only key        
                        for subsegmentKey in annotationPure:
                            segmentLabels += [annotationPure[subsegmentKey]]
                
            labelPositioner = MRSM_Presentation.ShowDescription.LabelPositioner(list(zip(segmentRefPoints,segmentLabels,segmentColors)))

            for gTuple in labelPositioner.getGraphicsTupleList():

                lineItem = self.imageScene.addLine(QLineF(gTuple[0],QPointF(gTuple[2])+QPointF(3,13))) #IH241002 HEURISTIC
                self.segmentAndAnnotationItems += [lineItem]

                rectItem:QGraphicsRectItem = gTuple[3]
                rect = self.imageScene.addRect(rectItem.rect())
                self.segmentAndAnnotationItems += [rect]

                textItem:QGraphicsTextItem = gTuple[1]
                label = self.imageScene.addText(textItem.document().toPlainText())
                label.setPos(gTuple[2])
                self.segmentAndAnnotationItems += [label]

                #IH241003 added
                targetDot = self.imageScene.addEllipse(QRectF(
                        QPointF(gTuple[0])+QPointF(-self.LabelPositioner.TARGETDOTRADIUS,-self.LabelPositioner.TARGETDOTRADIUS),
                        QPointF(gTuple[0])+QPointF(+self.LabelPositioner.TARGETDOTRADIUS,+self.LabelPositioner.TARGETDOTRADIUS) ))
                self.segmentAndAnnotationItems += [targetDot]

                #IH241001 HACK  apply style of rect to line
                c = gTuple[3].brush().color()
                rect.setBrush(c)
                targetDot.setBrush(c)
                lineItem.setPen(QPen(c,self.LabelPositioner.LINEWIDTH)) 

                #IH241002 layer adjustment for nice output. (pixmap is 0, segment polygons are 1)
                lineItem.setZValue(2)
                targetDot.setZValue(2)
                rectItem.setZValue(3)
                textItem.setZValue(4)

                # debug_message(f"TEXT -> {gTuple[1].document().toPlainText()}")
            
        def setActiveRadioButton(self,activeButton):
            """
            The bSagital, bCoronal, and bTransversal buttons work as a RadioButton group
            This method sets the active one.
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
    
    class ShowService():
        """
        Special service and maintenance tasks
        """
        IDLE_INACTIVITY_DURATION_SEC = int(1e6)  # IH241106 disable idle timer  (should be sys.maxint) 
                                                 # IH241108 int is here because 1e4 would default to float
        STATUS_UPDATE_PERIOD_MSEC = 2000

        def __init__(self,parent) -> None:

            self.grid :   QGridLayout   = parent.grid
            self.parent : QWidget       = parent
            self.serviceWidgets = []

            self.bgLabel = QLabel("",self.parent.MRSM_Window)
            self.grid.addWidget(self.bgLabel,0,0,4,32)  #IH240723 do not change this!
            
            #IH240729 This is necessary to prevent the image from voluntarily resizing
            self.bgLabel.setMinimumHeight(300)            
            self.bgLabel.setMaximumHeight(300)            
            self.bgLabel.setMinimumWidth(1460)            
            self.bgLabel.setMaximumWidth(1460)            

            self.serviceWidgets += [self.bgLabel]

            self.lHTMLText1 = QLabel(parent.lcls("#106"))
            self.lHTMLText1.setWordWrap(True)
            self.lHTMLText1.setMinimumWidth(1000)
            self.lHTMLText1.setMaximumWidth(1000)

            
            # self.grid.addWidget(self.lHTMLText1,0,0,4,27)
            self.saHTMLText1 = QScrollArea()
            self.saHTMLText1.setWidget(self.lHTMLText1)
            self.saHTMLText1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.saHTMLText1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.grid.addWidget(self.saHTMLText1,0,0,4,28)                                    
            self.saHTMLText1.verticalScrollBar().sliderMoved.connect(self.reset_idle_timer)
            self.lHTMLText1.setObjectName("lHTMLText1")  # this is for stylesheet reference 
            
            # self.infoWidgets += [self.lHTMLText1]
            self.serviceWidgets += [self.saHTMLText1]

            #IH241108 added
            self.status_update_timer = QTimer()
            self.status_update_timer.timeout.connect(self.on_status_update_timeout)
            

            self.deactivate()

        def activate(self):            
            for w in self.serviceWidgets:                                
                w.show()      
            self.parent.show()
            self.reset_idle_timer()  
            self.status_update_timer.start(self.STATUS_UPDATE_PERIOD_MSEC)
    
        def deactivate(self):
            for w in self.serviceWidgets:
                w.hide()
            self.status_update_timer.stop()                

        def reset_idle_timer(self):
            self.parent.idle_timer.stop()
            self.parent.idle_timer.start(self.IDLE_INACTIVITY_DURATION_SEC*1000)

        def on_status_update_timeout(self):
            currentAllValuesX = self.parent.hardwareController.magnetometer.getNormalizedReadingForAllSensors(MRSM_Magnetometer.MgMAxis.X)
            debug_message(f"Service Status Update:") 
            self.status_update_timer.start(self.STATUS_UPDATE_PERIOD_MSEC)            
    
    class ShowMagnetometer():
        """
        Controlling and presenting magnetometric measurement
        """
        IDLE_INACTIVITY_DURATION_SEC = int(1e6)  # IH241106 disable idle timer  (should be sys.maxint) 
                                                 # IH241108 int is here because 1e4 would default to float
        STATUS_UPDATE_PERIOD_MSEC = 200

        def __init__(self,parent) -> None:

            self.grid :   QGridLayout   = parent.grid
            self.parent : QWidget       = parent
            self.serviceMagnetometerWidgets = []

            self.bgLabel = QLabel("",self.parent.MRSM_Window)
            self.grid.addWidget(self.bgLabel,0,0,4,32)  #IH240723 do not change this!
            
            # #IH240729 This is necessary to prevent the image from voluntarily resizing
            self.bgLabel.setMinimumHeight(300)            
            self.bgLabel.setMaximumHeight(300)            
            self.bgLabel.setMinimumWidth(1460)            
            self.bgLabel.setMaximumWidth(1460)            

            self.serviceMagnetometerWidgets += [self.bgLabel]

            
            #IH241108 added
            #IH241108 added optionalization
            if self.parent.hasToUseMagFieldVisualization:
                from MRSM_FieldVisualizer import FieldPlotCanvas

                self.fieldPlotCanvas_Horizontal = FieldPlotCanvas(self.parent.hardwareController.magnetometer.MgMGeometry,
                                                    figureHeight=200,figureWidth=220,dpi=100,title='HORIZONTAL',
                                                    hasToIncludeColorbar=False)
                self.fieldPlotCanvas_Vertical   = FieldPlotCanvas(self.parent.hardwareController.magnetometer.MgMGeometry,
                                                    figureHeight=200,figureWidth=220,dpi=100,title='VERTICAL',
                                                    hasToIncludeColorbar=False)
                self.fieldPlotCanvas_Axial      = FieldPlotCanvas(self.parent.hardwareController.magnetometer.MgMGeometry,
                                                    figureHeight=200,figureWidth=220,dpi=100,title='AXIAL',
                                                    hasToIncludeColorbar=False)
                #IH241114 HACK we add another canvas just to show the colorbar
                self.fieldPlotCanvas_Colorbar    = FieldPlotCanvas(self.parent.hardwareController.magnetometer.MgMGeometry,
                                                    figureHeight=200,figureWidth=10,dpi=100,
                                                    hasToIncludeColorbar=True)

                #IH241113 TODO adapt grid coordinates for RPI display
                self.grid.addWidget(self.fieldPlotCanvas_Horizontal,    0,  3,      5, 7) 
                self.grid.addWidget(self.fieldPlotCanvas_Vertical,      0,  3+7,    5, 7)
                self.grid.addWidget(self.fieldPlotCanvas_Axial,         0,  3+7+7,  5, 7)

                self.grid.addWidget(self.fieldPlotCanvas_Colorbar,      0,  3+7+7+7,  5, 2)
                
                self.serviceMagnetometerWidgets += [self.fieldPlotCanvas_Horizontal]
                self.serviceMagnetometerWidgets += [self.fieldPlotCanvas_Vertical]
                self.serviceMagnetometerWidgets += [self.fieldPlotCanvas_Axial]
                self.serviceMagnetometerWidgets += [self.fieldPlotCanvas_Colorbar]


                self.plotLabel1 = QLabel("Components of the B<sub>0</sub> in the transversal plane (in relative units, cranial view)",
                                        self.parent.MRSM_Window,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                # self.grid.addWidget(self.plotLabel,1,5,8,1,10)
                #IH241114 we are ignoring here the Grid layouter, to save space
                self.plotLabel1.move(250,3) #IH241114 standard window width is 1480
                self.plotLabel1.resize(1000,17)
                self.serviceMagnetometerWidgets += [self.plotLabel1]
    
                if IsMagneticSensorEmulated:
                    self.Label2 = QLabel("SIMULATED VALUES!",
                                        self.parent.MRSM_Window,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
                    self.grid.addWidget(self.Label2,4,27,1,5)
                    self.serviceMagnetometerWidgets += [self.Label2]
    

            # IH241118 added
            spinBox_width  = 150
            spinBox_height = 48

            holderRotationAngleSpinBox_x = 1290
            holderRotationAngleSpinBox_y = 40

            self.holderRotationAngleSpinBox = QSpinBox(self.parent.MRSM_Window,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignCenter)
            self.holderRotationAngleSpinBox.move(holderRotationAngleSpinBox_x,holderRotationAngleSpinBox_y) 
            self.holderRotationAngleSpinBox.resize(spinBox_width,spinBox_height)
            self.holderRotationAngleSpinBox.setRange(-30,30)  # in degrees
            self.holderRotationAngleSpinBox.setSingleStep(10) 
            self.holderRotationAngleSpinBox.valueChanged.connect(self.holderRotationAngleSpinBox_valueChanged)
            self.serviceMagnetometerWidgets += [self.holderRotationAngleSpinBox]

            self.holderRotationAngleLabel = QLabel("Rotation angle [deg]",
                                        self.parent.MRSM_Window,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignCenter)
            self.holderRotationAngleLabel.move(holderRotationAngleSpinBox_x,holderRotationAngleSpinBox_y-20) 
            self.holderRotationAngleLabel.resize(spinBox_width,17)
            self.serviceMagnetometerWidgets += [self.holderRotationAngleLabel]
            

            holderAxialPositionSpinBox_x = 1290
            holderAxialPositionSpinBox_y = 120
            
            self.holderAxialPositionSpinBox = QSpinBox(parent=self.parent.MRSM_Window,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignCenter)
            self.holderAxialPositionSpinBox.move(holderAxialPositionSpinBox_x,holderAxialPositionSpinBox_y) 
            self.holderAxialPositionSpinBox.resize(spinBox_width,spinBox_height)
            self.holderAxialPositionSpinBox.setRange(0,150)  # in degrees
            self.holderAxialPositionSpinBox.setSingleStep(10) 
            self.holderAxialPositionSpinBox.valueChanged.connect(self.holderAxialPositionSpinBox_valueChanged)
            self.serviceMagnetometerWidgets += [self.holderAxialPositionSpinBox]

            self.holderAxialPositionLabel = QLabel("Axial position [mm]",
                                        self.parent.MRSM_Window,alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignCenter)
            self.holderAxialPositionLabel.move(holderAxialPositionSpinBox_x,holderAxialPositionSpinBox_y-20) 
            self.holderAxialPositionLabel.resize(spinBox_width,17)
            self.serviceMagnetometerWidgets += [self.holderAxialPositionLabel]

          
            self.bStore = self.parent.MRSM_PushButton(self.parent.lcls('STORE'),self.parent.MRSM_Window)
            self.bStore.move(1315,200) 
            self.bStore.clicked.connect(self.bStore_clicked)
            # self.grid.addWidget(self.bStore,0,28,8,10)
            self.serviceMagnetometerWidgets += [self.bStore]

            


            #IH241108 added
            self.status_update_timer = QTimer()
            self.status_update_timer.timeout.connect(self.on_status_update_timeout)
            
            self.deactivate()


        def holderRotationAngleSpinBox_valueChanged(self,value):
            self.setHolderAxialRotationAngle(value)

        def holderAxialPositionSpinBox_valueChanged(self,value):
            self.setHolderAxialPosition(value)

        def bStore_clicked(self):
            try:
                self.parent.hardwareController.magnetometer.storeCurrentReadings()
            except FileNotFoundError:
                self.parent.showMessageBoxCritical("Could not store file.")

        
        def activate(self):            
            for w in self.serviceMagnetometerWidgets:                                
                w.show()      
            self.parent.show()
            self.reset_idle_timer()  
            self.status_update_timer.start(self.STATUS_UPDATE_PERIOD_MSEC)
    
        def deactivate(self):
            for w in self.serviceMagnetometerWidgets:
                w.hide()
            self.status_update_timer.stop()                

        def reset_idle_timer(self):
            self.parent.idle_timer.stop()
            self.parent.idle_timer.start(self.IDLE_INACTIVITY_DURATION_SEC*1000)

        def on_status_update_timeout(self):
            #IH241108 added optionalization
            if self.parent.hasToUseMagFieldVisualization:
                self.fieldPlotCanvas_Horizontal.UpdatePlot(self.parent.hardwareController.magnetometer
                    .getNormalizedReadingForAllSensorsInScannerCoordinates(MRSM_Magnetometer.MgMOrientation.HORIZONTAL))
                self.fieldPlotCanvas_Vertical.UpdatePlot(self.parent.hardwareController.magnetometer
                    .getNormalizedReadingForAllSensorsInScannerCoordinates(MRSM_Magnetometer.MgMOrientation.VERTICAL))
                self.fieldPlotCanvas_Axial.UpdatePlot(self.parent.hardwareController.magnetometer
                    .getNormalizedReadingForAllSensorsInScannerCoordinates(MRSM_Magnetometer.MgMOrientation.AXIAL))
                
                self.fieldPlotCanvas_Colorbar.UpdatePlot(self.parent.hardwareController.magnetometer
                    .getNormalizedReadingForAllSensorsInScannerCoordinates(MRSM_Magnetometer.MgMOrientation.AXIAL))
            
            # debug_message(f"Status Update:") 
            self.status_update_timer.start(self.STATUS_UPDATE_PERIOD_MSEC)            
        

        def setHolderAxialRotationAngle(self,rotationAngleDeg):
            self.parent.hardwareController.magnetometer.setHolderAxialRotationAngle(rotationAngleDeg)
            #IH241108 added optionalization
            if self.parent.hasToUseMagFieldVisualization:  
                self.fieldPlotCanvas_Horizontal.updateScatteredPointPositions()
                self.fieldPlotCanvas_Vertical.updateScatteredPointPositions()
                self.fieldPlotCanvas_Axial.updateScatteredPointPositions()
                self.fieldPlotCanvas_Colorbar.updateScatteredPointPositions()
         

        def setHolderAxialPosition(self,axialPositionMm):
            self.parent.hardwareController.magnetometer.setHolderAxialPosition(axialPositionMm)
           

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
            hasToUseMagFieldVisualization: bool=False,
            ):
        self.language = language
        self.MRSM_Window = QWidget()
        self.hardwareController = hardwareController
        self.hasToUseMagFieldVisualization = hasToUseMagFieldVisualization

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
        self.MRSM_ImageBase = ImageBase(pixmapStandardSize=290,language_abbrev=LanguageAbbrev(language))

        #IH240723 the standard grid layout is ...(TODO)
        self.grid = QGridLayout()
        self.MRSM_Window.setLayout(self.grid)

        self.showIntro = self.ShowIntro(self)
        self.showMain = self.ShowMain(self)
        self.showIdle = self.ShowIdle(self)
        self.showInfo = self.ShowInfo(self)
        if HasToIncludeSegmentationPanel:
            self.showDescription = self.ShowDescription(self)
        self.showService = self.ShowService(self)
        
        if self.hasToUseMagFieldVisualization:
            	from MRSM_FieldVisualizer import FieldPlotCanvas
        self.showMagnetometer = self.ShowMagnetometer(self)        
        
        self.actual_idle_break_sec = 0

        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.on_idle_timeout)

        # 
        self.showIntro.activate()
        # IH241113 for debugging only
        # self.showMagnetometer.activate()

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
    
    def quit_intro_start_service(self):
        self.showIntro.deactivate()
        self.showService.activate() 

    def quit_intro_start_magnetometer(self):
        self.showIntro.deactivate()
        self.showMagnetometer.activate() 

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

    # IH241119 TODO reimplement this to allow setting parameters to the window 
    # for example: Qt Qt::WindowStaysOnTopHint

    def showMessageBoxCritical(self,text):
        button = QMessageBox.critical(
            self.MRSM_Window,
            "MRSM Problem",
            text,
            buttons=QMessageBox.StandardButton.Close,
            defaultButton=QMessageBox.StandardButton.Close,
        )
        
        # IH241118  c o n t i n u e   h e r e
        if button == QMessageBox.StandardButton.Close:
            return
