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
#      Last update: IH240819
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
#    For Raspberry Pi 5  documentation, see
#       https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#raspberry-pi-5-2
#
# 
#    For gpiozero documentation, see
#       https://gpiozero.readthedocs.io/en/stable/index.html
#
#


# TODOs
#-------------------------------------------------------------------------------

# BUGs
#
#   IH2407151 XXX
#
#-------------------------------------------------------------------------------

from enum import Enum

from MRSM_Globals import IsRaspberryPi5Emulated
from MRSM_Utilities import error_message, debug_message
from MRSM_Utilities import (
    TimerIterator,
)
from PyQt6.QtCore import (
    pyqtSlot,
    Qt
)
    

from gpiozero import (
    Device,
    LEDBoard
)

if IsRaspberryPi5Emulated:
    from gpiozero.pins.mock import MockFactory

from pygame import mixer
from MRSM_ImageBase import Organ, ImagingPlane


class SoundSample(Enum):
        NONE                    = 0
        KNEEMRISOUND            = 1
        HEADMRISOUND            = 2
        BODYMRISOUND            = 3
        HANDMRISOUND            = 4
        WHOLESPINEMRISOUND      = 5

class BoreLEDGroup(Enum):
        GROUP1                  =   1
        GROUP2                  =   2
        GROUP3                  =   3
        

class MRSM_Controller():

    def __init__(self) -> None:

        # audio 

        audioFile =  "resources/audio/MRIsounds/ytmp3free.cc_listen-to-mri-sounds-with-audio-frequency-analyzer-filmed-inside-the-mri-scan-room-youtubemp3free.org.mp3"
        self.audioPlayer = AudioPlayer(audioFile)
        self.organSound = {
            Organ.BODY:         SoundSample.BODYMRISOUND,
            Organ.KNEE:         SoundSample.KNEEMRISOUND,
            Organ.HEAD:         SoundSample.HEADMRISOUND,
            Organ.HAND:         SoundSample.HANDMRISOUND,
            Organ.WHOLESPINE:   SoundSample.WHOLESPINEMRISOUND,

            Organ.NONE:         SoundSample.NONE,
        }

        # Raspberry Pi GPIO

        self.rpiGPIO = RaspberryPiGPIO()
       
      
    def finalize(self):
         self.audioPlayer.finalize()

    def scanningSimulationShowStart(self, organ : Organ, imagingPlane : ImagingPlane) -> None:
        self.audioPlayer.play(self.organSound[organ])
        self.rpiGPIO.setBoreLEDIlluminationOn(True)
        self.rpiGPIO.setMainMagnetCoilOn(True)    

    def scanningSimulationShowStop(self) -> None:
        self.audioPlayer.stop()
        self.rpiGPIO.setBoreLEDIlluminationOn(False)
        self.rpiGPIO.setMainMagnetCoilOn(False)    


class AudioPlayer():

    def __init__(self,audioFile) -> None:

        self.sampleStartTime = {
             # start times of the respective sample in the file referred to above
             #IH240812 TODO tune up the exact times
             SoundSample.HEADMRISOUND:   (2*60.0 + 20.0) , # 2:20,  IH240812 just for debugging, TODO implement properly
             SoundSample.KNEEMRISOUND:   (5*60.0 +  0.0) , # 5:00,  IH240812 just for debugging, TODO implement properly
             SoundSample.HANDMRISOUND:   (5*60.0 + 40.0) , # 5:40,  IH240812 just for debugging, TODO implement properly
             SoundSample.BODYMRISOUND:   (6*60.0 + 25.0) , # 6:25,  IH240812 just for debugging, TODO implement properly
             SoundSample.WHOLESPINEMRISOUND:   (7*60.0 + 20.0) , # 7:20,  IH240812 just for debugging, TODO implement properly

             SoundSample.NONE:           0
        }
    
        self.mixer = mixer
        self.audioFile = audioFile
        self.mixer.init()   # IH240812 TODO  implement potential parameters here
        self.mixer.music.load(self.audioFile)

    def finalize(self):
        self.mixer.quit()

    def play(self, soundSample : SoundSample):
        #IH240812 TODO implement
        if soundSample!=SoundSample.NONE:
            self.mixer.music.play(start=self.sampleStartTime[soundSample])
    
    def stop(self):
        #IH240812 TODO implement
        self.mixer.music.stop()


class RaspberryPiGPIO():

    if IsRaspberryPi5Emulated:
            Device.pin_factory = MockFactory()

    boreLEDGroup1 = LEDBoard("GPIO17")     # RPI header pin 11
    boreLEDGroup2 = LEDBoard("GPIO27")     # RPI header pin 13
    boreLEDGroup3 = LEDBoard("GPIO22")     # RPI header pin 15

    mainMagnetCoil = LEDBoard(5)   #IH240812 for debugging only

    def __init__(self) -> None:
        
        self.HasToPlaySimpleShow = False
        
        self.LEDShowScenario = [
                {BoreLEDGroup.GROUP1: 1.0, BoreLEDGroup.GROUP2: 0.0, BoreLEDGroup.GROUP3: 0.0 },
                {BoreLEDGroup.GROUP1: 0.0, BoreLEDGroup.GROUP2: 1.0, BoreLEDGroup.GROUP3: 0.0 },
                {BoreLEDGroup.GROUP1: 0.0, BoreLEDGroup.GROUP2: 0.0, BoreLEDGroup.GROUP3: 1.0 },
                ]
        
    def setBoreLEDIlluminationOn(self,setON: bool) -> None:
        
        if setON:            
            if self.HasToPlaySimpleShow:
                # simple show
                self.boreLEDGroup1.on()
            else:
                # fancy show
                #IH240819 this should be done in the constructor only once, but it does not work for unknown reasons
                self.LEDShowScheduler = TimerIterator(values=self.LEDShowScenario)
                self.LEDShowScheduler.setInterval(1000)  # in milliseconds
                self.LEDShowScheduler.value_changed.connect(LEDShowStep)
                self.LEDShowScheduler.start() 
        else:            
            if self.HasToPlaySimpleShow:
                # simple show
                self.boreLEDGroup1.off()
            else:
                # fancy show
                self.LEDShowScheduler.stop()

        if IsRaspberryPi5Emulated:
            debug_message(f"Bore LEDs are now {'ON' if setON else 'OFF'}")

    def setMainMagnetCoilOn(self,setON: bool) -> None:
        RaspberryPiGPIO.mainMagnetCoil.on() if setON else RaspberryPiGPIO.mainMagnetCoil.off()
        if IsRaspberryPi5Emulated:
            debug_message(f"Main magnet is now {'ON' if setON else 'OFF'}")
    
@pyqtSlot(dict)
def LEDShowStep(d: dict):        
        if IsRaspberryPi5Emulated:
            print(f'G1> {d[BoreLEDGroup.GROUP1]}, G2> {d[BoreLEDGroup.GROUP2]}, G3> {d[BoreLEDGroup.GROUP3]}')
        else:
            #IH240819 simple implementation (on/off only)
            RaspberryPiGPIO.boreLEDGroup1.on() if d[BoreLEDGroup.GROUP1]>0.5 else RaspberryPiGPIO.boreLEDGroup1.off()
            RaspberryPiGPIO.boreLEDGroup2.on() if d[BoreLEDGroup.GROUP2]>0.5 else RaspberryPiGPIO.boreLEDGroup2.off()
            RaspberryPiGPIO.boreLEDGroup3.on() if d[BoreLEDGroup.GROUP3]>0.5 else RaspberryPiGPIO.boreLEDGroup3.off()

  

