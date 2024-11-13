#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  F i e l d  V i s u a l i z e r  .  p  y 
#
#
#      Last update: IH241113
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  N O T E S :
#
#   see
#       https://www.pythonguis.com/tutorials/pyqt6-plotting-matplotlib/
#       https://how2matplotlib.com/matplotlib-contour-from-points.html
#
#-------------------------------------------------------------------------------

import numpy as np
from scipy.interpolate import griddata

import matplotlib
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class FieldPlotCanvas(FigureCanvasQTAgg):

    gridSizeX = 100
    gridSizeY = 100

    def __init__(self,scatteredPointsDict,figureWidth,figureHeight,dpi=100,parent=None):
        figure = Figure(figsize=(figureWidth, figureHeight), dpi=dpi)
        self.axes = figure.add_subplot(111)
        super().__init__(figure)    

        self.scatteredPointDict = scatteredPointsDict 

        #IH241111 CHECK  I am not sure if the order "for p in self.scatteredPointDict]" is stable

        # Python 3.7 and later: Dictionaries maintain the insertion order of keys. 
        # This means that when you iterate over a dictionary, 
        # the keys will be returned in the order they were added.

        self.xScattered_Array = np.array([self.scatteredPointDict[p]['X'] for p in self.scatteredPointDict])
        self.yScattered_Array = np.array([self.scatteredPointDict[p]['Y'] for p in self.scatteredPointDict])

        # create regular grid
        self.xRegularGrid_Array = np.linspace(self.xScattered_Array.min(),self.xScattered_Array.max(),FieldPlotCanvas.gridSizeX) 
        self.yRegularGrid_Array = np.linspace(self.yScattered_Array.min(),self.yScattered_Array.max(),FieldPlotCanvas.gridSizeY) 
        self.xRegularGrid_Array,self.yRegularGrid_Array = np.meshgrid(self.xRegularGrid_Array,self.yRegularGrid_Array)
        
        
    def SetFieldValuesInScatteredPoints(self,valuesDict):
        #IH241113
        # Interpolate scattered data to regular grid
        self.valueScattered_Array = np.array([valuesDict[p] for p in valuesDict])
        self.valueRegularGrid_Array = griddata((self.xScattered_Array, self.yScattered_Array), self.valueScattered_Array, 
                                      (self.xRegularGrid_Array, self.yRegularGrid_Array), method='cubic')

    def updateValues(self,valuesDict):
        self.SetFieldValuesInScatteredPoints(valuesDict)
        #IH241113 TODO update plot