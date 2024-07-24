#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  I  m  a  g  e  B  a  s  e  .  p  y 
#
#
#      Last update: IH240724
#-------------------------------------------------------------------------------

from enum import Enum

from PyQt6.QtCore import (
    Qt
)

from PyQt6.QtGui import (
    QPixmap
)

class Organ(Enum):
        NONE        =   0
        HEAD        =   1
        KNEE        =   2
        ABDOMEN     =   3

class ImagingPlane(Enum):
        SAGITTAL    =   0
        CORONAL     =   1
        TRANSVERSAL =   2
    

class ImageBase():
    
    def __init__(self,pixmapStandardSize=290) -> None:

        self.pixmapStandardSize = pixmapStandardSize

        self.MRimages= [
            {'organ':  Organ.HEAD, 
             'imagingPlane' : ImagingPlane.SAGITTAL, 
                'JPGFileRelativePath': "resources/images/Free-Max/Head/2a_Head_t1_tse_dark-fl_sag_p4_DRB.jpg",
                'pixmapOriginal':   None,  # to be populated later
                'pixmapScaled':    None   # to be populated later
            },  
            {'organ':  Organ.HEAD, 
             'imagingPlane' : ImagingPlane.CORONAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Head/2b_Head_t2_tse_cor_p4_DRB.jpg",
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },
            {'organ':  Organ.HEAD, 
             'imagingPlane' : ImagingPlane.TRANSVERSAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Head/2c_Head_t2_tse_tra_p4.jpg",
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },
            {'organ':  Organ.KNEE, 
             'imagingPlane' : ImagingPlane.SAGITTAL, 
                'JPGFileRelativePath': "resources/images/Free-Max/Knee/13d_Knee_pd_tse_fs_sag_p4_DRB.jpg",
                'pixmapOriginal':   None,  
                'pixmapScaled':    None   
            },  
            {'organ':  Organ.KNEE	, 
             'imagingPlane' : ImagingPlane.CORONAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Knee/13b_Knee_pd_tse_fs_cor_p4_DRB.jpg",
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },
            {'organ':  Organ.KNEE, 
             'imagingPlane' : ImagingPlane.TRANSVERSAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Knee/13c_Knee_pd_tse_fs_tra_p4_DRB.jpg", 
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },  
        ]

        for im in self.MRimages:
              #IH240724 WARNING  We do not check file accessibility here
              im['pixmapOriginal'] = QPixmap(im['JPGFileRelativePath'])
              im['pixmapScaled'] = im['pixmapOriginal'].scaled(
                    self.pixmapStandardSize,self.pixmapStandardSize,
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                    
    def getScaledPixmap(self,organ: Organ,imagingPlane : ImagingPlane):
        for im in self.MRimages:
            if im['organ']==organ and im['imagingPlane']==imagingPlane:
                 return im['pixmapScaled'] 
        return None