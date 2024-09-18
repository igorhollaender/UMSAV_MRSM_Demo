#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  S  e  g  m  e  n  t  a  t  i  o  n   F  a  c  t  o  r  y  .  p  y 
#
#
#      Last update: IH240918
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  N O T E S :
#
#  Important!
#
#  When working in the SegmentationWorkbench.svg in Inkscape, set the following Inkscape preference:
#  Preferences -> Input/Output -> SVG output -> Path data -> Path String Format: ABSOLUTE
#
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# Segmentation guides
#
#  BRAIN:
#     https://hpy555medim.blogspot.com/2012/10/mri-of-brain.html
#     https://www.imaios.com/en/e-anatomy/brain/mri-axial-brain
#
#  ABDOMEN
#     https://radiologykey.com/mri-of-the-abdomen/
#
#-------------------------------------------------------------------------------

import xml.etree.ElementTree as ET
import re

from PyQt6.QtGui import (
    QPolygonF,
)
from PyQt6.QtCore import (    
    QPointF,
)

from MRSM_Utilities import debug_message
from MRSM_TextContent import LanguageAbbrev


class SegmentationFactory:

    def __init__(self,SVGsegmentationWorkbenchFilename) -> None:

        self.SVGsegmentationWorkbenchFilename = SVGsegmentationWorkbenchFilename
        self.segmentationWorkbenchTree = ET.parse(self.SVGsegmentationWorkbenchFilename)
        self.segmentationWorkbenchTreeRoot = self.segmentationWorkbenchTree.getroot()
        
        #IH240912 for debugging only

        # IH240912 for supported XPath subset, see
        # https://docs.python.org/2/library/xml.etree.elementtree.html#xpath-support
        # for example:  debug_message(self.segmentationWorkbenchTree.findall(".//*[contains(@id,'SEGMENT_')]")) # this is not supported

        inkscapeNamespaces = {
            'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
            'svg':"http://www.w3.org/2000/svg"
                      }
        self.segmentDict = {}
        for pathElement in   self.segmentationWorkbenchTree.findall(".//svg:path",inkscapeNamespaces):
            id = pathElement.get('id')
            if id.startswith("SEGMENT_"):
                self.segmentDict[id] = {}
                self.segmentDict[id]['segmentSVGPath']=pathElement.get('d')
                m = re.search('^SEGMENT_(?P<organ>[A-Z]+)_(?P<imagingPlane>[A-Z]+)_(?P<segment>[A-Z]+)(?P<subsegment>([_A-Z]+)*)',id)
                if m is not None:
                    debug_message(f"   O: {m.group('organ')}   P: {m.group('imagingPlane')}  S: {m.group('segment')}  SS: {m.group('subsegment')}" )
                    self.segmentDict[id]['organ']= m.group('organ')
                    self.segmentDict[id]['imagingPlane']= m.group('imagingPlane')
                    self.segmentDict[id]['segment']= m.group('segment')
                    if m.group('subsegment')!= "":
                        self.segmentDict[id]['subsegment']= m.group('subsegment')[1:] #IH240913 first character is a '_'                
                    else:
                        self.segmentDict[id]['subsegment']=None
                    # find the respective bounding box
                    for rectElement in self.segmentationWorkbenchTree.findall(".//svg:rect",inkscapeNamespaces):
                        BBid = rectElement.get('id')
                        if BBid != f"BB_{self.segmentDict[id]['organ']}_{self.segmentDict[id]['imagingPlane']}":
                            continue
                        self.segmentDict[id]['boundingBox']={}
                        self.segmentDict[id]['boundingBox']['x']=rectElement.get('x')
                        self.segmentDict[id]['boundingBox']['y']=rectElement.get('y')
                        self.segmentDict[id]['boundingBox']['width']=rectElement.get('width')
                        self.segmentDict[id]['boundingBox']['height']=rectElement.get('height')

                    assert 'boundingBox' in self.segmentDict[id],"No respective bounding box found" # IH240916 we must have one bounding box
                    assert float(self.segmentDict[id]['boundingBox']['width'])>0,"Bounding box rectangle has zero width"
                    assert float(self.segmentDict[id]['boundingBox']['height'])>0,"Bounding box rectangle has zero height"

                    # find the respective annotation
                    thisAnnotation = None
                    for textElement in   self.segmentationWorkbenchTree.findall(".//svg:text",inkscapeNamespaces):
                        ANNOid = textElement.get('id')
                        m = re.search('^ANNOTATION_(?P<language>[A-Z][A-Z])_(?P<organ>[A-Z]+)_(?P<imagingPlane>[A-Z]+)_(?P<segment>[A-Z]+)(?P<subsegment>([_A-Z]+)*)',ANNOid)


                        #IH240918 PROBLEM here, we have to access the application language

                        #IH240918 for debugging only
                        app_language_abbrev = LanguageAbbrev.SK

                        if m is not None and (
                            m.group('organ') == self.segmentDict[id]['organ'] and
                            m.group('imagingPlane') == self.segmentDict[id]['imagingPlane'] and
                            m.group('segment') == self.segmentDict[id]['segment'] and
                            (m.group('subsegment')[1:] == self.segmentDict[id]['subsegment'] if  self.segmentDict[id]['subsegment']is not None else True ) and
                            LanguageAbbrev[m.group('language')] == app_language_abbrev ):  

                            tspanElement = textElement.find("./svg:tspan",inkscapeNamespaces)
                            if tspanElement is not None:
                                thisAnnotation=tspanElement.text

                    assert thisAnnotation is not None, f"No annotation found for {id},  language {app_language_abbrev}"  

                    #IH240918 TODO simplify the data structure: QPolygons should only be one single QPolygon, not dict of dicts 
                    if 'QPolygons' not in self.segmentDict[id]:
                        self.segmentDict[id]['QPolygons'] = {}
                    if self.segmentDict[id]['segment'] not in self.segmentDict[id]['QPolygons']:
                        self.segmentDict[id]['QPolygons'][self.segmentDict[id]['segment']] = {}
                    if self.segmentDict[id]['subsegment'] not in self.segmentDict[id]['QPolygons'][self.segmentDict[id]['segment']]:
                        self.segmentDict[id]['QPolygons'][self.segmentDict[id]['segment']] = {}
                    self.segmentDict[id]['QPolygons'][self.segmentDict[id]['segment']][self.segmentDict[id]['subsegment']]=SegmentationFactory.inkscapePathToQPolygon(
                                            self.segmentDict[id]['segmentSVGPath'],self.segmentDict[id]['boundingBox'])
                    
                    if 'annotation' not in self.segmentDict[id]:
                        self.segmentDict[id]['annotation'] = {}
                    if self.segmentDict[id]['segment'] not in self.segmentDict[id]['annotation']:
                        self.segmentDict[id]['annotation'][self.segmentDict[id]['segment']] = {}
                    if self.segmentDict[id]['subsegment'] not in self.segmentDict[id]['annotation'][self.segmentDict[id]['segment']]:
                        self.segmentDict[id]['annotation'][self.segmentDict[id]['segment']] = {}
                    self.segmentDict[id]['annotation'][self.segmentDict[id]['segment']][self.segmentDict[id]['subsegment']]=thisAnnotation
                    

        self.UnitTest()

    def getSegmentQPolygonsAndAnnotations(self,organ, imagingPlane):
        """
        returns list of QPolygon's for given organ and imagingPlane (key is subsegment name of 'None', value is QPolygon)
        and list of corresponding annotations
        """
        qPolygons = []
        annotations = []
        for segmentId in self.segmentDict.keys():
            if f"_{organ.name}_" in segmentId and f"_{imagingPlane.name}_" in segmentId:
                qPolygons += [self.segmentDict[segmentId]['QPolygons']]
                annotations += [self.segmentDict[segmentId]['annotation']]
        return qPolygons, annotations
    
    

    def getAnnotations(self,organ,imagingPlane):
        """
        returns list of dicts, key is  ...
        """
        annotations = []
        #IH240918 TODO
        return annotations
    
 
    def inkscapePathToQPolygon(inkscapePath: str, inkscapeBBRect):
        """
        returns QPolygonF object with normalized coordinates (0,0) is upper left corner, (1,1) is lower right corner
        """
        reDecimalNumber = r"(-?\d*\.?\d*)"  #IH240918 Python 3.12 issues a SyntaxWarning here:  invalid escape sequence '\d'; that's why the leading 'r'
        debug_message(inkscapePath)
        debug_message(inkscapeBBRect)
        debug_message(f" BBX: {inkscapeBBRect['x']}  BBY: {inkscapeBBRect['y']}")

        polygon = QPolygonF()
        for pointCoords in re.finditer(f"{reDecimalNumber},{reDecimalNumber}",inkscapePath):
            (coordXstr,coordYstr) = pointCoords.group().split(",")  
            coordX = (float(coordXstr)-float(inkscapeBBRect['x']))/float(inkscapeBBRect['width'])
            coordY = (float(coordYstr)-float(inkscapeBBRect['y']))/float(inkscapeBBRect['height'])
            debug_message(f" X: {coordX}  Y: {coordY}")
            polygon += QPointF(coordX,coordY)
        return polygon 
        
    def UnitTest(self):
        debug_message(self.segmentDict)


