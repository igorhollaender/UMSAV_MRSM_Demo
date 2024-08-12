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
#      Last update: IH240812
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

from pygame import mixer
from MRSM_ImageBase import Organ, ImagingPlane


class SoundSample(Enum):
        NONE                    = 0
        KNEEMRISOUND            = 1
        HEADMRISOUND            = 2


class MRSM_Controller():

    def __init__(self) -> None:

        audioFile =  "resources/audio/MRIsounds/ytmp3free.cc_listen-to-mri-sounds-with-audio-frequency-analyzer-filmed-inside-the-mri-scan-room-youtubemp3free.org.mp3"
        self.audioPlayer = AudioPlayer(audioFile)

        self.organSound = {
            Organ.ABDOMEN:      SoundSample.NONE,   # IH240812 TODO
            Organ.KNEE:         SoundSample.KNEEMRISOUND,
            Organ.HEAD:         SoundSample.HEADMRISOUND,

            Organ.NONE:         SoundSample.NONE,
        }

      
    def finalize(self):
         self.audioPlayer.finalize()

    def scanningSimulationShowStart(self, organ : Organ, imagingPlane : ImagingPlane) -> None:
        self.audioPlayer.play(self.organSound[organ])
        # self.audioPlayer.play(self.organSound[Organ.KNEE])


    def scanningSimulationShowStop(self) -> None:
        self.audioPlayer.stop()

class AudioPlayer():

      
    def __init__(self,audioFile) -> None:

        self.sampleStartTime = {
             # start times of the respective sample in the file referred to above
             #IH240812 TODO tune up the exact times
             SoundSample.HEADMRISOUND:   (2*60.0 + 20.0) , # 2:20,  IH240812 just for debugging, TODO implement properly
             SoundSample.KNEEMRISOUND:   (8*60.0 + 15.0) , # 8:15,  IH240812 just for debugging, TODO implement properly

             SoundSample.NONE:           0
        }
    
        self.mixer = mixer
        self.audioFile = audioFile
        self.mixer.init()   # IH240812 TODO  implement potential parameters here
        self.mixer.music.load(self.audioFile)

    def finalize(self):
        mixer.quit()

    def play(self, soundSample : SoundSample):
        #IH240812 TODO implement
        if soundSample!=SoundSample.NONE:
            mixer.music.play(start=self.sampleStartTime[soundSample])
    
    def stop(self):
        #IH240812 TODO implement
        mixer.music.stop()




