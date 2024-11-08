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
#      Last update: IH241108
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
#   For smbus2 documentation, see
#       https://pypi.org/project/smbus2/
#


# TODOs
#-------------------------------------------------------------------------------

# BUGs
#
#   IH2407151 XXX
#
#-------------------------------------------------------------------------------

from enum import Enum
from time import sleep, time
from math import sin,cos,pi,radians
from random import random, uniform

from MRSM_Globals import IsRaspberryPi5Emulated, IsMagneticSensorEmulated
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

            Organ.KNEE2:        SoundSample.KNEE2MRISOUND,

            Organ.NONE:         SoundSample.NONE,
        }

        # Raspberry Pi GPIO

        self.rpiGPIO = RaspberryPiGPIO()

        # Magnetometer

        self.magnetometer = MRSM_Magnetometer()
       
      
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
            print(f'G1> {d[BoreLEDGroup.GROUP1]}, G2> {d[BoreLEDGroup.GROUP2]}, G3> {d[BoreLEDGroup.GROUP3]}')            
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

    def __init__(self) -> None:
          
        self.MgMGeometry = {
             
                #   for sensor geometry, see 
                #       resources/images/diverse/ChipHolder Geometry.pdf
                #

                # 'sensorPositionName':
                #   position OF THE REFERENCE POINT is primarily given in polar coordinates (Radius,Angle)
                #   origin is in the center of the scanner bore
                #   'Orientation' gives angle of the sensor in degrees, 0 is pointing up, clockwise

                #   'Radius'    in millimeters
                #   'Angle'     in degrees, 0 is pointing up, clockwise
                #   'Angle'     in degrees, 0 is pointing up, clockwise
                #   'X','Y'     are carthesian coordinates OF THE SENSOR ACTIVE POINT, will be computed 
                
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

        if not IsMagneticSensorEmulated:
            self.availableSensors = set(['1','2'])  #IH241108 use actually availale sensor positions
            self.signalEmulator = None
        else:
            self.availableSensors = set(self.MgMGeometry.keys())  
            self.signalEmulator = MRSM_Magnetometer.A31301_SimpleEmulator()
        
        # debug_message(self.availableSensors)

        # calculate X,Y coordinates of THE SENSOR ACTIVE POINT 
        #  X points to the right, Y points up, origin is in the center
        for sensorPos in self.MgMGeometry:
            self.MgMGeometry[sensorPos]['X'] = (
                self.MgMGeometry[sensorPos]['Radius']*sin(radians(self.MgMGeometry[sensorPos]['Angle']))+
                MRSM_Magnetometer.ChipOffset_mm*sin(radians(self.MgMGeometry[sensorPos]['Orientation'])))
            self.MgMGeometry[sensorPos]['Y'] = (
                self.MgMGeometry[sensorPos]['Radius']*cos(radians(self.MgMGeometry[sensorPos]['Angle']))+
                MRSM_Magnetometer.ChipOffset_mm*cos(radians(self.MgMGeometry[sensorPos]['Orientation'])))
        
            # debug_message(f'{sensorPos}: X={self.MgMGeometry[sensorPos]["X"]}, Y={self.MgMGeometry[sensorPos]["Y"]})')
    
    class MgMAxis(Enum):
         X  =   1
         Y  =   2
         Z  =   3
    
    def getReading(self,sensorPos,axis: MgMAxis) -> int:
        if IsMagneticSensorEmulated:
            return self.signalEmulator.getReading(sensorPos,axis)
        else:
            return 1234.5678
            # see A31301 datasheet, p.28
            # Output registers to use:
            #
            #   X_CHANNEL_15B (0x1E:0x1F[14:0])
            #       This register holds the 15-bit signed output of the X-axis sensor output.
            #   Y_CHANNEL_15B (0x20:0x21[14:0])
            #       This register holds the 15-bit signed output of the Y-axis sensor output.
            #   Z_CHANNEL_15B (0x22:0x23[14:0])
            #       This register holds the 15-bit signed output of the Z-axis sensor output

            # IH241107  TODO implement

    def getNormalizedReading(self,sensorPos,axis: MgMAxis) -> float:
         """
         returns reading from -1.00 to +1.00, 1 is the max range of the sensor
         """
         return self.getReading(sensorPos,axis)/MRSM_Magnetometer.A31301_maxReadingRange
    
    class A31301_SimpleEmulator():
        """
        Simple generator of time-dependent signal reading
        """

        def __init__(self) -> None:
            pass
         
        def getReading(self,sensorPos,axis) -> int:
            if axis==MRSM_Magnetometer.MgMAxis.X:                 
                peakValue = int(MRSM_Magnetometer.A31301_maxReadingRange*0.5)
            if axis==MRSM_Magnetometer.MgMAxis.Z:                 
                peakValue = int(MRSM_Magnetometer.A31301_maxReadingRange*0.2)
            if axis==MRSM_Magnetometer.MgMAxis.Y:
                peakValue = int(sin(time()/pi/10)*MRSM_Magnetometer.A31301_maxReadingRange)                 
            spreadCoefficient = {
                    # sensorPos -> value from 0 to 1
                    "1" :  1.00,
                    "C" :  0.80,                    
                    "7" :  0.80,                    
                    "6" :  0.30,                    
                    "D" :  0.30,                    
                    "2" :  0.30,                    
                    }
            spreadFactor = 0.1
            if sensorPos in spreadCoefficient:
                spreadFactor = spreadCoefficient[sensorPos]                
            randomFactor = uniform(0.9,1.0)            
            returnValue = max(-MRSM_Magnetometer.A31301_maxReadingRange,min(MRSM_Magnetometer.A31301_maxReadingRange,
                        peakValue*spreadFactor*randomFactor))
            return returnValue
                    