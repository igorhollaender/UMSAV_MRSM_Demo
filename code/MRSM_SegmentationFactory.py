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
#      Last update: IH240913
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


import xml.etree.ElementTree as ET
import re

from MRSM_Utilities import debug_message


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

            #  IH240913   c o n t i n u e.  h e r e    
            
        self.UnitTest()

    def getSegmentQPolygons(self,organ, imagingPlane):
        """
        Returns list of QPolygon's for given organ and imagingPlane
        """
        for segmentId in self.segmentDict.keys:
            if f"_{organ.name}_" in segmentId and f"_{imagingPlane.name}_" in segmentId:
                pass
        return []
 
    def inkscapePathToQPolygon(inkscapePath: str, inkscapeBBRect: str):
        return None
        
    def UnitTest(self):
        debug_message(self.segmentDict)


