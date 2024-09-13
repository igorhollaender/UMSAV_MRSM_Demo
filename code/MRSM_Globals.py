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
#      Last update: IH240913
#-------------------------------------------------------------------------------


__version__                 = "MRSM_Demo IH240913a"

IsWaveShareDisplayEmulated  = True   # set to False for real application
IsRaspberryPi5Emulated      = True  # set to False for real application
IsQtMultimediaAvailable     = False  # IH240722 I had problems 
                                     # installing QtMultimedia on Raspberry OS,
                                     # so this is a workaround
HasToShowExitButton         = True    # set to False for real application
HasToShowGoIdleButton       = False   # set to False for real application

HasToIncludeSegmentationPanel  = True   # set to False to run the stable version (Segmentation is experimental feature)

VerboseLevel                = 2     # 0 is complete muted, 1 is standard, 2 is for debugging


#-------------------------------------------------------------------------------
