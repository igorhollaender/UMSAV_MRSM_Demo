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
#      Last update: IH240925
#-------------------------------------------------------------------------------


from enum import Enum

from PyQt6.QtCore import (
    Qt
)

from PyQt6.QtGui import (
    QPixmap
)

from MRSM_TextContent import LanguageAbbrev

from MRSM_SegmentationFactory import SegmentationFactory

class Organ(Enum):
        NONE        =   0
        HEAD        =   1
        KNEE        =   2
        BODY        =   3
        HAND        =   4
        WHOLESPINE  =   5

class ImagingPlane(Enum):
        ARBITRARY   =   0
        SAGITTAL    =   1
        CORONAL     =   2
        TRANSVERSAL =   3
    

class ImageBase():
    
    def __init__(self,pixmapStandardSize=290,language_abbrev=LanguageAbbrev.EN) -> None:

        self.pixmapStandardSize = pixmapStandardSize
        self.language_abbrev = language_abbrev

        self.MRimages= [
            {'organ':  Organ.HEAD, 
             'imagingPlane' : ImagingPlane.SAGITTAL, 
                'JPGFileRelativePath': "resources/images/Free-Max/Head/2a_Head_t1_tse_dark-fl_sag_p4_DRB.jpg",
                'pixmapOriginal':   None,  # to be populated later
                'pixmapScaled':    None,   # to be populated later
                'annotation':   {
                     # IH240916 this is just an example template, the populating is done programmatically
                    'segmentation': 
                        [   
                            {
                            'descriptionHTML': "",
                            'calloutPolygons':[[],[]],
                            'regionPolygons':[[],[]],
                            'style': {'brush': None, 'pen': None, } 
                            },
                            {
                            'descriptionHTML': "",
                            'calloutPolygons':[[],[]],
                            'regionRolygons':[[],[]],
                            'style': {'brush': None, 'pen': None, }
                            },
                        ],
                    },
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
            {'organ':  Organ.BODY	, 
             'imagingPlane' : ImagingPlane.CORONAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Body/3c_Body_t2_tse_cor_p4_mbh_DRB.jpg",
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },
            {'organ':  Organ.BODY, 
             'imagingPlane' : ImagingPlane.TRANSVERSAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Body/3b_Body_t2_tse_tra_p4_mbh_DRB.jpg", 
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },  
            {'organ':  Organ.HAND, 
             'imagingPlane' : ImagingPlane.SAGITTAL, 
                'JPGFileRelativePath': "resources/images/Free-Max/Hand/11d_Hand_t2_tse_sag_p4_DRB.jpg",
                'pixmapOriginal':   None,  
                'pixmapScaled':    None   
            },  
            {'organ':  Organ.HAND, 
             'imagingPlane' : ImagingPlane.CORONAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Hand/11a_Hand_t1_tse_cor_p4_DRB.jpg",
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },
            {'organ':  Organ.HAND, 
             'imagingPlane' : ImagingPlane.TRANSVERSAL,
                'JPGFileRelativePath': "resources/images/Free-Max/Hand/11c_Hand_pd_tse_fs_tra_p4_DRB.jpg", 
                'pixmapOriginal':   None,
                'pixmapScaled':    None,
            },
            {'organ':  Organ.WHOLESPINE,
             'imagingPlane' : ImagingPlane.SAGITTAL, 
                'JPGFileRelativePath': "resources/images/Free-Max/WholeSpine/1a_Whole_spine_T1_TSE_2steps.jpg",
                'pixmapOriginal':   None,  
                'pixmapScaled':    None   
            },
        ]

        for im in self.MRimages:
              #IH240724 WARNING  We do not check file accessibility here
              im['pixmapOriginal'] = QPixmap(im['JPGFileRelativePath'])
              im['pixmapScaled'] = im['pixmapOriginal'].scaled(
                    self.pixmapStandardSize,self.pixmapStandardSize,
                    aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)

        # populating the segmentation data

        self.segmentationFactory = SegmentationFactory("resources/images/Free-Max/Segmentation/Segmentation Workbench.svg",language_abbrev=self.language_abbrev)

                    
    def getScaledPixmap(self,organ: Organ,imagingPlane : ImagingPlane):
        for im in self.MRimages:
            if im['organ']==organ and im['imagingPlane']==imagingPlane:
                 return im['pixmapScaled'] 
        return None
    
    def getAnnotation(self,organ: Organ, imagingPlane: ImagingPlane):
        for im in self.MRimages:
            if im['organ']==organ and im['imagingPlane']==imagingPlane:
                 return im['annotation'] 
        return None
