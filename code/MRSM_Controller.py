#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#      The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  C  o  n  t  r  o  l  l  e  r  .  p  y 
#
#
#      Last update: IH241205
# #
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
#   For smbus2 documentation, see
#       https://pypi.org/project/smbus2/
#
#   For i2c-tools documentation see
#       https://thelinuxcode.com/i2c-linux-utilities/


#-------------------------------------------------------------------------------
#   The I2C interface has to be enabled by
#    $ sudo dtparam i2c_arm=on
#
#   The I2C clock frequency can be set by
#    $ sudo dtparam i2c_arm_baudrate=1000000
#   and then restart i2c by (this is just IH's speculation)
#    $ sudo dtparam i2c_arm=on
#
#  see https://forums.raspberrypi.com/viewtopic.php?t=360996

#   
# TODOs
#-------------------------------------------------------------------------------

# BUGs
#
#   IH2407151 XXX
#
#-------------------------------------------------------------------------------

from enum import Enum
from time import sleep, time, asctime
from math import sin,cos,pi,radians
from random import random, uniform


from MRSM_Globals import IsRaspberryPi5Emulated, IsMagneticSensorEmulated, __version__
from MRSM_Utilities import error_message, debug_message
from MRSM_DataExporter import JSONDataExporter
from MRSM_Utilities import (
    TimerIterator,
)
from PyQt6.QtCore import (
    pyqtSlot,
    Qt
)
    
from gpiozero import (
    Device,
    LEDBoard, 
)

#IH241107  use "pip install smbus2" if not installed
if not IsMagneticSensorEmulated:
    from smbus2 import SMBus

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

        KNEE2MRISOUND           = 6 #IH241007 added

        XMASTREESOUND           = 7 #IH2411122 added

class BoreLEDGroup(Enum):
        GROUP1                  =   1
        GROUP2                  =   2
        GROUP3                  =   3
        
class MRSM_Controller():

    def __init__(self,exportDirectory='.') -> None:

        # audio 

        audioFile =  "resources/audio/MRIsounds/ytmp3free.cc_listen-to-mri-sounds-with-audio-frequency-analyzer-filmed-inside-the-mri-scan-room-youtubemp3free.org.mp3"
        
        self.audioPlayer = AudioPlayer(audioFile)
        self.organSound = {
            Organ.BODY:         SoundSample.BODYMRISOUND,
            Organ.KNEE:         SoundSample.KNEEMRISOUND,
            Organ.HEAD:         SoundSample.HEADMRISOUND,
            Organ.HAND:         SoundSample.HANDMRISOUND,
            Organ.WHOLESPINE:   SoundSample.WHOLESPINEMRISOUND,

            Organ.KNEE2:        SoundSample.KNEE2MRISOUND,
            Organ.XMASTREE:     SoundSample.XMASTREESOUND,

            Organ.NONE:         SoundSample.NONE,
        }

        # Raspberry Pi GPIO

        self.rpiGPIO = RaspberryPiGPIO()

        # Magnetometer

        self.exportDirectory = exportDirectory
        self.magnetometer = MRSM_Magnetometer(self.exportDirectory)

      
    def finalize(self):
         self.audioPlayer.finalize()
         LEDShowStep(RaspberryPiGPIO.LEDShowStep_AllOff)

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

             SoundSample.KNEE2MRISOUND:   (5*60.0 +  0.0) ,  #IH241007 added
             SoundSample.XMASTREESOUND:   (0.0) ,  #IH241007 added

             SoundSample.NONE:           0
        }
    
        self.mixer = mixer
        self.audioFile = audioFile
        self.mixer.init()   # IH240812 TODO  implement potential parameters here
        self.mixer.music.load(self.audioFile)

    def finalize(self):
        self.mixer.quit()


    def playTest(self,hasToplayIndefinitely=False):
        testAudioFile = "resources/audio/diverse/stereo-test.mp3"
        self.mixer.music.unload()
        self.mixer.music.load(testAudioFile)
        self.mixer.music.play(loops=-1 if hasToplayIndefinitely else 0)

    def play(self, soundSample : SoundSample):
        
        # IH241122 HACK
        if soundSample==SoundSample.XMASTREESOUND:   
            thisAudioFile = "resources/audio/diverse/jingle-bells-orchestra-127418.mp3"
        else:
            thisAudioFile = self.audioFile
        
        if soundSample!=SoundSample.NONE:
            self.mixer.music.unload()
            self.mixer.music.load(thisAudioFile)
            self.mixer.music.play(start=self.sampleStartTime[soundSample])
    
    def stop(self):
        self.mixer.music.stop()    

class MRSMGPIOPin(LEDBoard):        
    """
    IH240820 
    For some reason (probably due to our electrical connections)
    our LEDs work opposite to the logic (on is off and vice versa)
    This class inverts the behaviour.
    """
    def __init__(self, *pins, pwm=False, active_high=True, initial_value=False, _order=None, pin_factory=None, **named_pins):
          super().__init__(*pins, pwm=pwm, active_high=active_high, initial_value=initial_value, _order=_order, pin_factory=pin_factory, **named_pins)
    
    def on(self):
         super().off()

    def off(self):
         super().on()
     
class RaspberryPiGPIO():

    if IsRaspberryPi5Emulated:
            Device.pin_factory = MockFactory()

    
    boreLEDGroup1 = MRSMGPIOPin("GPIO21")     # RPI header pin 40, relay IN1, white
    boreLEDGroup2 = MRSMGPIOPin("GPIO26")     # RPI header pin 37, relay IN2, grey
    boreLEDGroup3 = MRSMGPIOPin("GPIO20")     # RPI header pin 38, relay IN3, violet

    # IH240820  the following currently not used
    relaySwitch4 = MRSMGPIOPin("GPIO19")     # RPI header pin 35, relay IN4, blue
    relaySwitch5 = MRSMGPIOPin("GPIO16")     # RPI header pin 36, relay IN5, green
    relaySwitch6 = MRSMGPIOPin("GPIO13")     # RPI header pin 33, relay IN6, yellow
    relaySwitch7 = MRSMGPIOPin("GPIO6")      # RPI header pin 31, relay IN7, orange
    relaySwitch8 = MRSMGPIOPin("GPIO12")     # RPI header pin 32, relay IN8, brown
    
    LEDShowStep_AllOn  = {BoreLEDGroup.GROUP1: 1.0, BoreLEDGroup.GROUP2: 1.0, BoreLEDGroup.GROUP3: 1.0 }
    LEDShowStep_AllOff = {BoreLEDGroup.GROUP1: 0.0, BoreLEDGroup.GROUP2: 0.0, BoreLEDGroup.GROUP3: 0.0 }
      
    mainMagnetCoil = relaySwitch8           #IH240821 TODO adapt to real hardware

    def __init__(self) -> None:
        
        self.HasToPlaySimpleShow = False    #IH240820 True was for debugging only
        
        
        self.LEDShowScenario_ScanStarting = [
                RaspberryPiGPIO.LEDShowStep_AllOn, RaspberryPiGPIO.LEDShowStep_AllOff,
                RaspberryPiGPIO.LEDShowStep_AllOn, RaspberryPiGPIO.LEDShowStep_AllOff,
                RaspberryPiGPIO.LEDShowStep_AllOn, RaspberryPiGPIO.LEDShowStep_AllOff
                ]
        
        self.LEDShowScenario_ScanRunning = [
                {BoreLEDGroup.GROUP1: 1.0, BoreLEDGroup.GROUP2: 0.0, BoreLEDGroup.GROUP3: 0.0 },
                {BoreLEDGroup.GROUP1: 0.0, BoreLEDGroup.GROUP2: 1.0, BoreLEDGroup.GROUP3: 0.0 },
                {BoreLEDGroup.GROUP1: 0.0, BoreLEDGroup.GROUP2: 0.0, BoreLEDGroup.GROUP3: 1.0 },
                {BoreLEDGroup.GROUP1: 1.0, BoreLEDGroup.GROUP2: 1.0, BoreLEDGroup.GROUP3: 0.0 },
                {BoreLEDGroup.GROUP1: 0.0, BoreLEDGroup.GROUP2: 1.0, BoreLEDGroup.GROUP3: 1.0 },
                {BoreLEDGroup.GROUP1: 1.0, BoreLEDGroup.GROUP2: 0.0, BoreLEDGroup.GROUP3: 1.0 },
                ]
        
        self.LEDShowScenario_ScanFinished = [
                RaspberryPiGPIO.LEDShowStep_AllOn, RaspberryPiGPIO.LEDShowStep_AllOff,
                RaspberryPiGPIO.LEDShowStep_AllOn, RaspberryPiGPIO.LEDShowStep_AllOff,
                RaspberryPiGPIO.LEDShowStep_AllOn, RaspberryPiGPIO.LEDShowStep_AllOff
                ]
                
        LEDShowStep(RaspberryPiGPIO.LEDShowStep_AllOff)
    
        
    def setBoreLEDIlluminationOn(self,setON: bool) -> None:
        
        if setON:            
            if self.HasToPlaySimpleShow:
                # simple show
                self.boreLEDGroup1.on()
            else:
                # fancy show
                
                #IH240819 Trivial scheduled show
                for step in self.LEDShowScenario_ScanStarting:
                     LEDShowStep(step)
                     sleep(0.3)

                #IH240819 this should be done in the constructor only once, but it does not work for unknown reasons                
                self.LEDShowScheduler = TimerIterator(values=self.LEDShowScenario_ScanRunning,infinite_loop=True)
                self.LEDShowScheduler.setInterval(150)  # in milliseconds
                self.LEDShowScheduler.value_changed.connect(LEDShowStep)                
                self.LEDShowScheduler.start() 

        else:            
            if self.HasToPlaySimpleShow:
                # simple show
                self.boreLEDGroup1.off()
            else:
                # fancy show
                self.LEDShowScheduler.stop()

                #IH240819 Trivial scheduled show
                for step in self.LEDShowScenario_ScanFinished:
                     LEDShowStep(step)
                     sleep(0.15)

                #IH240821 OBSOLETE
                # self.LEDShowScheduler = TimerIterator(values=self.LEDShowScenario_ScanFinished,infinite_loop=False)
                # self.LEDShowScheduler.setInterval(150)  # in milliseconds
                # self.LEDShowScheduler.value_changed.connect(LEDShowStep)                
                # self.LEDShowScheduler.start() 

                LEDShowStep(RaspberryPiGPIO.LEDShowStep_AllOff)
                
        if IsRaspberryPi5Emulated:
            debug_message(f"Bore LEDs are now {'ON' if setON else 'OFF'}")

    def setMainMagnetCoilOn(self,setON: bool) -> None:
        RaspberryPiGPIO.mainMagnetCoil.on() if setON else RaspberryPiGPIO.mainMagnetCoil.off()
        if IsRaspberryPi5Emulated:
            debug_message(f"Main magnet is now {'ON' if setON else 'OFF'}")
    
@pyqtSlot(dict)
def LEDShowStep(d: dict):        
        if IsRaspberryPi5Emulated:
            debug_message(f'G1> {d[BoreLEDGroup.GROUP1]}, G2> {d[BoreLEDGroup.GROUP2]}, G3> {d[BoreLEDGroup.GROUP3]}')            
        else:
            # IH240819 simple implementation (on/off only)            
            RaspberryPiGPIO.boreLEDGroup1.on() if d[BoreLEDGroup.GROUP1]>0.5 else RaspberryPiGPIO.boreLEDGroup1.off()
            RaspberryPiGPIO.boreLEDGroup2.on() if d[BoreLEDGroup.GROUP2]>0.5 else RaspberryPiGPIO.boreLEDGroup2.off()
            RaspberryPiGPIO.boreLEDGroup3.on() if d[BoreLEDGroup.GROUP3]>0.5 else RaspberryPiGPIO.boreLEDGroup3.off()
 
class MRSM_Magnetometer():

    Geometry_Radius1_mm    =   22.50
    Geometry_Radius2_mm    =   15.00
    Geometry_Radius3_mm    =   4.50

    ChipOffset_mm          =   1.0  # distance from reference plane (containing reference point) to sensor active point
    A31301_maxReadingRange =   pow(2,15-1)-1  # the A31301 delivers signed 15bit values



    def __init__(self,exportDirectory='.') -> None:
        
        self.holderRotationAngleDeg     = 0.0   # rotation angle is degrees, 0 is pointing up, clockwise in the cranial view
        self.holderAxialPositionMm      = 0.0   # axial position in M, TODO specify 
        self.exportDirectory            = exportDirectory
        self.dataExporter = JSONDataExporter(self.exportDirectory)

        self.MgMGeometry = {
             
                #   for sensor geometry, see 
                #       resources/images/diverse/ChipHolder Geometry.pdf
                #

                # 'sensorPositionName':
                #   position OF THE REFERENCE POINT is primarily given in polar coordinates (Radius,Angle)
                #   origin is in the center of the scanner bore
                #   'Orientation' gives angle of the sensor in degrees, 0 is pointing up, clockwise
                #           looking at the sensor holder from the side of sensors
                #           (pin 1 is always nearer to the observer)

                #   'Radius'    in millimeters
                #   'Angle'     in degrees, 0 is pointing up, clockwise
                #   'Angle'     in degrees, 0 is pointing up, clockwise
                #   'X','Y'     are carthesian coordinates OF THE SENSOR ACTIVE POINT, will be computed, in millimeters,
        
                
                '1':    {'Radius': MRSM_Magnetometer.Geometry_Radius1_mm, 
                         'Angle': 0*60.0, 'Orientation': 0*60.0,
                         'X':None, 'Y':None },
                '2':    {'Radius': MRSM_Magnetometer.Geometry_Radius1_mm, 
                         'Angle': 1*60.0, 'Orientation': 1*60.0,
                         'X':None, 'Y':None },
                '3':    {'Radius': MRSM_Magnetometer.Geometry_Radius1_mm, 
                         'Angle': 2*60.0, 'Orientation': 2*60.0,
                         'X':None, 'Y':None },
                '4':    {'Radius': MRSM_Magnetometer.Geometry_Radius1_mm, 
                         'Angle': 3*60.0, 'Orientation': 3*60.0,
                         'X':None, 'Y':None },
                '5':    {'Radius': MRSM_Magnetometer.Geometry_Radius1_mm, 
                         'Angle': 4*60.0, 'Orientation': 4*60.0,
                         'X':None, 'Y':None },
                '6':    {'Radius': MRSM_Magnetometer.Geometry_Radius1_mm, 
                         'Angle': 5*60.0, 'Orientation': 5*60.0,
                         'X':None, 'Y':None },
                '7':    {'Radius': MRSM_Magnetometer.Geometry_Radius2_mm, 
                         'Angle': 0*60.0+30.0, 'Orientation': 0*60.0-60.0,
                         'X':None, 'Y':None },
                '8':    {'Radius': MRSM_Magnetometer.Geometry_Radius2_mm, 
                         'Angle': 1*60.0+30.0, 'Orientation': 1*60.0-60.0,
                         'X':None, 'Y':None },
                '9':    {'Radius': MRSM_Magnetometer.Geometry_Radius2_mm, 
                         'Angle': 2*60.0+30.0, 'Orientation': 2*60.0-60.0,
                         'X':None, 'Y':None },
                'A':    {'Radius': MRSM_Magnetometer.Geometry_Radius2_mm, 
                         'Angle': 3*60.0+30.0, 'Orientation': 3*60.0-60.0,
                         'X':None, 'Y':None },
                'B':    {'Radius': MRSM_Magnetometer.Geometry_Radius2_mm, 
                         'Angle': 4*60.0+30.0, 'Orientation': 4*60.0-60.0,
                         'X':None, 'Y':None },
                'C':    {'Radius': MRSM_Magnetometer.Geometry_Radius2_mm, 
                         'Angle': 5*60.0+30.0, 'Orientation': 5*60.0-60.0,
                         'X':None, 'Y':None },

                'D':    {'Radius': MRSM_Magnetometer.Geometry_Radius3_mm, 
                         'Angle': 0.0, 'Orientation': 0.0,
                         'X':None, 'Y':None },
                'E':    {'Radius': MRSM_Magnetometer.Geometry_Radius3_mm, 
                         'Angle': 180.0, 'Orientation': 180.0,
                         'X':None, 'Y':None },

                'F':    {'Radius': 2.36, 
                         'Angle': 0.0, 'Orientation': 0.0,
                         'X':None, 'Y':None },
        }

        self.MgMsensorI2CAddress = {
                '1':    96,      # AD1 = 0.00 ,  AD0 =  0.00       * Vcc
                '2':    97,      # AD1 = 0.00 ,  AD0 =  0.33       * Vcc
                '3':    98,      # AD1 = 0.00 ,  AD0 =  0.67       * Vcc
                '4':    99,      # AD1 = 0.00 ,  AD0 =  1.00       * Vcc

                '5':   100,      # AD1 = 0.33 ,  AD0 =  0.00       * Vcc
                '6':   101,      # AD1 = 0.33 ,  AD0 =  0.33       * Vcc
                '7':   102,      # AD1 = 0.33 ,  AD0 =  0.67       * Vcc
                '8':   103,      # AD1 = 0.33 ,  AD0 =  1.00       * Vcc

                '9':   104,      # AD1 = 0.67 ,  AD0 =  0.00       * Vcc
                'A':   105,      # AD1 = 0.67 ,  AD0 =  0.33       * Vcc
                'B':   106,      # AD1 = 0.67 ,  AD0 =  0.67       * Vcc
                'C':   107,      # AD1 = 0.67 ,  AD0 =  1.00       * Vcc

                'D':   108,      # AD1 = 1.00 ,  AD0 =  0.00       * Vcc
                'E':   109,      # AD1 = 1.00 ,  AD0 =  0.33       * Vcc
                'F':   110,      # AD1 = 1.00 ,  AD0 =  0.67       * Vcc
        }

        self.MgMsensorI2CRegister = {
             'TEMPERATURE_12B_MSB' :  0x1c,
             'TEMPERATURE_12B_LSB' :  0x1d,

             'X_CHANNEL_15B_MSB' :  0x1e,
             'X_CHANNEL_15B_LSB' :  0x1f,
             'Y_CHANNEL_15B_MSB' :  0x20,
             'Y_CHANNEL_15B_LSB' :  0x21,
             'Z_CHANNEL_15B_MSB' :  0x22,
             'Z_CHANNEL_15B_LSB' :  0x23,
            }

        if not IsMagneticSensorEmulated:
            self.availableSensors = set(['4'])  # IH241108 use actually available sensor positions
                                                    # IH241204 1 is 0x60, 4 is 0x63
            self.signalEmulator = None
            self.smbus = SMBus(1)   #using I2C bus 1
        else:
            self.availableSensors = set(self.MgMGeometry.keys())  
            self.signalEmulator = MRSM_Magnetometer.A31301_SimpleEmulator(self)
        
        # debug_message(self.availableSensors)

        self.calculateSensorXY()

        # # calculate X,Y coordinates of THE SENSOR ACTIVE POINT in the Scanner coordinate system,
        # #  X (Horizontal) points to the right, Y (Vertical) points up, origin is in the center
        # for sensorPos in self.MgMGeometry:
        #     self.MgMGeometry[sensorPos]['X'] = (
        #         self.MgMGeometry[sensorPos]['Radius']*sin(radians(self.MgMGeometry[sensorPos]['Angle']))+
        #         MRSM_Magnetometer.ChipOffset_mm*sin(radians(self.MgMGeometry[sensorPos]['Orientation'])))
        #     self.MgMGeometry[sensorPos]['Y'] = (
        #         self.MgMGeometry[sensorPos]['Radius']*cos(radians(self.MgMGeometry[sensorPos]['Angle']))+
        #         MRSM_Magnetometer.ChipOffset_mm*cos(radians(self.MgMGeometry[sensorPos]['Orientation'])))
        
        #     # debug_message(f'{sensorPos}: X={self.MgMGeometry[sensorPos]["X"]}, Y={self.MgMGeometry[sensorPos]["Y"]})')
    
        #IH241111 for debugging only
        if not IsMagneticSensorEmulated:            
            doAgain = False  # IH241204 disabled
            while doAgain:
                debug_message(  f'X: {self.getReading("4",self.MgMAxis.X)},  ' +
                                f'Y: {self.getReading("4",self.MgMAxis.Y)},  ' +
                                f'Z: {self.getReading("4",self.MgMAxis.Z)}')
                sleep(1)
                doAgain = False            

    def calculateSensorXY(self):
        """
        calculate X,Y coordinates of THE SENSOR ACTIVE POINT in the Scanner coordinate system,
        X (Horizontal) points to the right, Y (Vertical) points up, origin is in the center
        """
        for sensorPos in self.MgMGeometry:
            self.MgMGeometry[sensorPos]['X'] = (
                self.MgMGeometry[sensorPos]['Radius']*sin(radians(self.MgMGeometry[sensorPos]['Angle']+self.holderRotationAngleDeg))+
                MRSM_Magnetometer.ChipOffset_mm*sin(radians(self.MgMGeometry[sensorPos]['Orientation']+self.holderRotationAngleDeg)))
            self.MgMGeometry[sensorPos]['Y'] = (
                self.MgMGeometry[sensorPos]['Radius']*cos(radians(self.MgMGeometry[sensorPos]['Angle']+self.holderRotationAngleDeg))+
                MRSM_Magnetometer.ChipOffset_mm*cos(radians(self.MgMGeometry[sensorPos]['Orientation']+self.holderRotationAngleDeg)))
        
            # debug_message(f'{sensorPos}: X={self.MgMGeometry[sensorPos]["X"]}, Y={self.MgMGeometry[sensorPos]["Y"]})')
    

    class MgMAxis(Enum):
         """
         in the Sensor coordinate frame
         """
         X  =   1
         Y  =   2
         Z  =   3
    
    class MgMOrientation(Enum):
         """
         in the Scanner coordinate frame
         """
         HORIZONTAL = 1
         VERTICAL   = 2
         AXIAL      = 3

    def setHolderAxialRotationAngle(self,rotationAngleDeg):
        """
        rotation angle is degrees, 0 is showing up, clockwise in the cranial view
        """
        self.holderRotationAngleDeg = rotationAngleDeg
        self.calculateSensorXY()
    
    def setHolderAxialPosition(self,axialPositionMm):
        """
        currently, this has no effect on calculations, just logging in export file
        """
        self.holderAxialPositionMm = axialPositionMm 
    
    
    def storeCurrentReadings(self):
        """
        export data to a JSON file with (fixed file name, will be overwitten each time)
        """
        self.exportFilename="MRSM_readings.json"  #IH241118 for debugging only
        self.readingsDict = {
            "_comment":                 """
This is an MRSM export file.
""",
            "MRSM_version":             __version__,
            "datestamp":                asctime(),
            "sensorGeometry":           self.MgMGeometry,
            "holderAxialPositionMM":    self.holderAxialPositionMm,
            "holderRotationAngleDeg":   self.holderRotationAngleDeg,
            "readings_comment":         """
The readings are given in the sensor's own coordinate system. 
The values are relative to a maximum possible readout (sensor max range)",
""",
            "readings_X":               self.getNormalizedReadingForAllSensors(MRSM_Magnetometer.MgMAxis.X),
            "readings_Y":               self.getNormalizedReadingForAllSensors(MRSM_Magnetometer.MgMAxis.Y),
            "readings_Z":               self.getNormalizedReadingForAllSensors(MRSM_Magnetometer.MgMAxis.Z),
        }

        self.dataExporter.export(self.readingsDict, self.exportFilename)

    def getTemperatureReadingDegC(self,sensorPos) -> float:
        if IsMagneticSensorEmulated:
            return self.signalEmulator.getTemperatureReadingDegC(sensorPos)
        else:
            I2C_address = self.MgMsensorI2CAddress[sensorPos]
            Temperature_readout = self.smbus.read_word_data(I2C_address,   self.MgMsensorI2CRegister['TEMPERATURE_12B_MSB'])    
            Temperature_readout &= 0x0FFF
            if (Temperature_readout & 0x0800):
                Temperature_readout -= 0x1000                    
            # for formula, see A31303 Datasheet, p.13
            Temperature_DegC = float(Temperature_readout)/8052 + 25
            
            return Temperature_DegC
               
        
    def getReading(self,sensorPos,axis: MgMAxis,stopTime:bool=False) -> int:

        # sleep(0.5) # IH241204 for debugging only, make a forced pause between subsequent readings

        # IH241203 the stopTime parameter is only relevant for simulation        
        if IsMagneticSensorEmulated:
            return self.signalEmulator.getReading(sensorPos,axis,stopTime)
        else:
            # see A31301 datasheet, p.28
            # Output registers to use:
            #
            #   X_CHANNEL_15B (0x1E:0x1F[14:0])
            #       This register holds the 15-bit signed output of the X-axis sensor output.
            #   Y_CHANNEL_15B (0x20:0x21[14:0])
            #       This register holds the 15-bit signed output of the Y-axis sensor output.
            #   Z_CHANNEL_15B (0x22:0x23[14:0])
            #       This register holds the 15-bit signed output of the Z-axis sensor output


            # IH241204 for experimenting
            READOUT_METHOD_BYTE = True
            READOUT_METHOD_WORD = False

            I2C_address = self.MgMsensorI2CAddress[sensorPos]

            if READOUT_METHOD_BYTE:
                                
                MSB_X_readout = self.smbus.read_byte_data(I2C_address,   self.MgMsensorI2CRegister['X_CHANNEL_15B_MSB'])
                LSB_X_readout = self.smbus.read_byte_data(I2C_address,   self.MgMsensorI2CRegister['X_CHANNEL_15B_LSB'])
                    
                MSB_Y_readout = self.smbus.read_byte_data(I2C_address,   self.MgMsensorI2CRegister['Y_CHANNEL_15B_MSB'])
                LSB_Y_readout = self.smbus.read_byte_data(I2C_address,   self.MgMsensorI2CRegister['Y_CHANNEL_15B_LSB'])
                    
                MSB_Z_readout = self.smbus.read_byte_data(I2C_address,   self.MgMsensorI2CRegister['Z_CHANNEL_15B_MSB'])
                LSB_Z_readout = self.smbus.read_byte_data(I2C_address,   self.MgMsensorI2CRegister['Z_CHANNEL_15B_LSB'])

                debug_message(f'MSB_X_readout> {MSB_X_readout},LSB_X_readout> {LSB_X_readout}' )
                     
                value_X = ((MSB_X_readout & 0x7F) << 8) | (LSB_X_readout & 0xFF)
                value_Y = ((MSB_Y_readout & 0x7F) << 8) | (LSB_Y_readout & 0xFF)
                value_Z = ((MSB_Z_readout & 0x7F) << 8) | (LSB_Z_readout & 0xFF)

                # IH241205 PROBLEM still not correct conversion
                
                if(value_X & 0x4000):
                        value_X -= 0x8000
                if(value_Y & 0x4000):
                        value_Y -= 0x8000
                if(value_Z & 0x4000):
                        value_Z -= 0x8000

            if READOUT_METHOD_WORD:
                
                Word_X_readout = self.smbus.read_word_data(I2C_address,   self.MgMsensorI2CRegister['X_CHANNEL_15B_MSB'])    
                Word_Y_readout = self.smbus.read_word_data(I2C_address,   self.MgMsensorI2CRegister['Y_CHANNEL_15B_MSB'])
                Word_Z_readout = self.smbus.read_word_data(I2C_address,   self.MgMsensorI2CRegister['Z_CHANNEL_15B_MSB'])
                # debug_message(f'Word_X_readout> {Word_X_readout}')

                value_X = Word_X_readout & 0x7FFF
                value_Y = Word_Y_readout & 0x7FFF
                value_Z = Word_Z_readout & 0x7FFF

                if (value_X & 0x4000):                    
                    value_X -= 0x8000
                if (value_Y & 0x8000):                                                   
                    value_Y -= 0x8000
                if (value_Z & 0x4000):                                        
                    value_Z -= 0x8000

            if axis==self.MgMAxis.X:
                value = value_X
            if axis==self.MgMAxis.Y:
                value = value_Y
            if axis==self.MgMAxis.Z:
                value = value_Z

            return value
        

    def getNormalizedReading(self,sensorPos,axis: MgMAxis) -> float:
         """
         returns reading from -1.00 to +1.00, 1 is the max range of the sensor
         """
         return self.getReading(sensorPos,axis)/MRSM_Magnetometer.A31301_maxReadingRange
    
    def getNormalizedReadingForAllSensors(self,axis:MgMAxis) -> dict:
        retDict = {}
        for sensorPos in self.MgMGeometry:
            retDict[sensorPos] = self.getNormalizedReading(sensorPos,axis)
            
        return retDict
    
    def getNormalizedReadingForAllSensorsInScannerCoordinates(self,orientation:MgMOrientation) -> dict:
        retDict = {}
        for sensorPos in self.MgMGeometry:
            readingX = self.getNormalizedReading(sensorPos,MRSM_Magnetometer.MgMAxis.X)
            readingY = self.getNormalizedReading(sensorPos,MRSM_Magnetometer.MgMAxis.Y)
            readingZ = self.getNormalizedReading(sensorPos,MRSM_Magnetometer.MgMAxis.Z)

            # sensor mount geometry:
            #   if pin 1 is pointing in the orientation of patient head (cranial direction):
            #       X is in the AXIAL direction, showing to patient head (cranial direction)
            #       Y in in the tangential direction
            #       Z is in the radial direction, pointing out of the center
            #   XYZ is  LEFTHANDED system (see A31301 datasheet)

            #IH241113 CHECK these formulae:
            if orientation==MRSM_Magnetometer.MgMOrientation.AXIAL:
                retDict[sensorPos] = readingX
            if orientation==MRSM_Magnetometer.MgMOrientation.VERTICAL:
                retDict[sensorPos] = (
                        readingZ * cos(radians(self.MgMGeometry[sensorPos]['Orientation']))
                      + readingY * sin(radians(self.MgMGeometry[sensorPos]['Orientation'])))
            if orientation==MRSM_Magnetometer.MgMOrientation.HORIZONTAL:
                retDict[sensorPos] = (
                        readingY * cos(radians(self.MgMGeometry[sensorPos]['Orientation'])) 
                      - readingZ * sin(radians(self.MgMGeometry[sensorPos]['Orientation'])))
            
        return retDict
    
    class A31301_SimpleEmulator():
        """
        Simple generator of time-dependent signal reading
        """

        def __init__(self,magnetometer) -> None:
            self.magnetometer = magnetometer                    
            self.timeForSensor = {}
            self.randomFactorForSensor = {}
            for s in self.magnetometer.MgMGeometry.keys():
                self.timeForSensor[s] = time()
                self.randomFactorForSensor[s] = uniform(0.9,1.0) 

        def getTemperatureReadingDegC(self,sensorPos) -> float:        
            return 25.0 + uniform(-0.5,+0.5) 
         
        def getReading(self,sensorPos,axis,stopTime:bool=False) -> int:
            """
            IH241203 the stopTime parameter is used to simulate readings comming immediately after each other,
            so the return value should be the same
            """
            """
            IH241203 BUG not working as expected
            temporary workaround: only use stopTime=False
            """
            
            if not stopTime:                
                self.timeForSensor[sensorPos] = time()
                self.randomFactorForSensor[sensorPos] = uniform(0.9,1.0)            

            if axis==MRSM_Magnetometer.MgMAxis.X:           
                peakValue = int(sin(self.timeForSensor[sensorPos]/pi/10)*MRSM_Magnetometer.A31301_maxReadingRange)         
            if axis==MRSM_Magnetometer.MgMAxis.Z:                 
                peakValue = int(MRSM_Magnetometer.A31301_maxReadingRange*0.7)
            if axis==MRSM_Magnetometer.MgMAxis.Y:
                peakValue = int(MRSM_Magnetometer.A31301_maxReadingRange*0.9)
                             
            spreadCoefficient = {
                    # sensorPos -> value from 0 to 1
                    "1" :  1.00,
                    "C" :  0.80,                    
                    "7" :  0.80,                    
                    "6" :  0.30,                    
                    "D" :  0.30,                    
                    "2" :  0.30,

                    "3" :  0.11, "4" :  0.12, "5" :  0.13, "8" :  0.14,
                    "9" :  0.15, "A" :  0.16, "B" :  0.17, "E" :  0.18, "F" :  0.19,
                    }
            spreadFactor = 0.1
            if sensorPos in spreadCoefficient:
                spreadFactor = spreadCoefficient[sensorPos]                

            returnValue = int(max(-MRSM_Magnetometer.A31301_maxReadingRange,min(MRSM_Magnetometer.A31301_maxReadingRange,
                        peakValue*spreadFactor*self.randomFactorForSensor[sensorPos])))
            return returnValue
                    