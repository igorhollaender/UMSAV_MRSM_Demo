#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  G l o b a l s  .  p  y 
#
#
#      Last update: IH240812
#-------------------------------------------------------------------------------
import time


__version__                 = "MRSM_Demo IH240812a"

IsWaveShareDisplayEmulated  = True   # set to False for real application
IsRaspberryPi5Emulated      = True  # set to False for real application
IsQtMultimediaAvailable     = False  # IH240722 I had problems 
                                     # installing QtMultimedia on Raspberry OS,
                                     # so this is a workaround
HasToShowExitButton         = True   # set to False for real application
HasToShowGoIdleButton       = True   # set to False for real application

VerboseLevel                = 2     # 0 is complete muted, 1 is standard, 2 is for debugging


#-------------------------------------------------------------------------------
# Global utilities

def error_message(m):
    if VerboseLevel>0:
        print(m)
    
def debug_message(m):
    if VerboseLevel>1:
        print(f"MRSM debug: {time.asctime()}: {m}")
