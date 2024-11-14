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
#      Last update: IH241114
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

from MRSM_Utilities import debug_message, error_message

class FieldPlotCanvas(FigureCanvasQTAgg):

    gridSizeX = 100
    gridSizeY = 100

    def __init__(self,scatteredPointsDict,figureWidth,figureHeight,dpi=100,parent=None,
                 title='',
                 hasToIncludeColorbar=True):
        
        self.scatteredPointDict = scatteredPointsDict 
        self.title = title
        self.hasToIncludeColorbar = hasToIncludeColorbar

        self.figure = Figure(figsize=(figureWidth, figureHeight), dpi=dpi)
        self.axes = self.figure.add_subplot(111)        
        super().__init__(self.figure)    

        
        #IH241111 I was not sure if the order "for p in self.scatteredPointDict]" is stable. But this is in doc:
        # Python 3.7 and later: Dictionaries maintain the insertion order of keys. 
        # This means that when you iterate over a dictionary, 
        # the keys will be returned in the order they were added.

        self.xScattered_Array = np.array([self.scatteredPointDict[p]['X'] for p in self.scatteredPointDict])
        self.yScattered_Array = np.array([self.scatteredPointDict[p]['Y'] for p in self.scatteredPointDict])

        # create regular grid
        self.xRegularGrid_Array = np.linspace(self.xScattered_Array.min(),self.xScattered_Array.max(),FieldPlotCanvas.gridSizeX) 
        self.yRegularGrid_Array = np.linspace(self.yScattered_Array.min(),self.yScattered_Array.max(),FieldPlotCanvas.gridSizeY) 
        self.xRegularGrid_Array,self.yRegularGrid_Array = np.meshgrid(self.xRegularGrid_Array,self.yRegularGrid_Array)
        
        self.UpdatePlot({k: 0 for k in self.scatteredPointDict.keys()}) #use zero initaial values

    def UpdatePlot(self,valuesDict):

        self.valueScattered_Array = np.array([float(valuesDict[p]) for p in valuesDict])
        self.valueRegularGrid_Array = griddata((self.xScattered_Array, self.yScattered_Array), self.valueScattered_Array, 
                                      (self.xRegularGrid_Array, self.yRegularGrid_Array), method='cubic',fill_value=np.nan)

        # self.levels = [-0.5,-0.1,0.0,0.1,0.5]
        self.levels = np.linspace(-1.0,1.0,21)
        # self.levels = [-0.5,-0.02,0.0,0.02,0.5]
        
        self.axes.cla()
        # self.axes = self.figure.add_subplot(111)

        # show color field map
        self.contourfPlot = self.axes.contourf(
                        self.xRegularGrid_Array,
                        self.yRegularGrid_Array,
                        self.valueRegularGrid_Array,
                        levels=self.levels,
                        extend='both',
                        cmap='viridis'
        )

        # show isolines
        self.contourPlot = self.axes.contour(
                        self.xRegularGrid_Array,
                        self.yRegularGrid_Array,
                        self.valueRegularGrid_Array,
                        levels=self.levels,
                        colors='k',
                        linewidths=0.5
        )
        plt.clabel(self.contourPlot, inline=1, fontsize=8)

        # show measuring points
        self.scatterPlot = self.axes.scatter(
                        self.xScattered_Array,
                        self.yScattered_Array,
                        c='red',
                        s=10
        )

        self.axes.set_axis_off()
        self.axes.set_title(self.title)
        self.axes.axis('equal')
        if self.hasToIncludeColorbar:
            #IH241114 PROBLEM HERE This does not work
            
            if hasattr(self,'colorbar'):
                self.colorbar.ax.remove()
            # self.colorbar = plt.colorbar(self.contourfPlot)

        self.draw()
       