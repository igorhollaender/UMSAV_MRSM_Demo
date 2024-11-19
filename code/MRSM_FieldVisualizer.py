#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#      The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  F i e l d  V i s u a l i z e r  .  p  y 
#
#
#      Last update: IH241119
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
from matplotlib.patches import Circle,Polygon
from matplotlib.collections import PatchCollection

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

        self.figure = Figure(figsize=(figureWidth, figureHeight), dpi=dpi,facecolor='blue')
        self.axes = self.figure.add_subplot(111)        
        self.axes.set_position([-0.1,-0.1,1.2,1.2])
        super().__init__(self.figure)    

        self.updateScatteredPointPositions()
     
    def updateScatteredPointPositions(self):
       
        #IH241111 I was not sure if the order "for p in self.scatteredPointDict" is stable. But this is in doc:
        # Python 3.7 and later: Dictionaries maintain the insertion order of keys. 
        # This means that when you iterate over a dictionary, 
        # the keys will be returned in the order they were added.

        self.xScattered_Array = np.array([self.scatteredPointDict[p]['X'] for p in self.scatteredPointDict])
        self.yScattered_Array = np.array([self.scatteredPointDict[p]['Y'] for p in self.scatteredPointDict])

        # create regular grid
        self.xRegularGrid_Array = np.linspace(self.xScattered_Array.min(),self.xScattered_Array.max(),FieldPlotCanvas.gridSizeX) 
        self.yRegularGrid_Array = np.linspace(self.yScattered_Array.min(),self.yScattered_Array.max(),FieldPlotCanvas.gridSizeY) 
        self.xRegularGrid_Array,self.yRegularGrid_Array = np.meshgrid(self.xRegularGrid_Array,self.yRegularGrid_Array)
        
        self.UpdatePlot({k: 0 for k in self.scatteredPointDict.keys()}) #use zero initial values


    def UpdatePlot(self,valuesDict):

        self.valueScattered_Array = np.array([float(valuesDict[p]) for p in valuesDict])
        self.valueRegularGrid_Array = griddata((self.xScattered_Array, self.yScattered_Array), self.valueScattered_Array, 
                                      (self.xRegularGrid_Array, self.yRegularGrid_Array), method='cubic',fill_value=np.nan)

        # self.levels = [-0.5,-0.1,0.0,0.1,0.5]
        self.levels = np.linspace(-1.0,1.0,21)
        
        # purge old plots
        self.axes.cla()
       
        # show color field map
        self.contourfPlot = self.axes.contourf(
                        self.xRegularGrid_Array,
                        self.yRegularGrid_Array,
                        self.valueRegularGrid_Array,
                        levels=self.levels,
                        extend='both',
                        cmap='PiYG'
                        #IH241114 for a choice of cmap's, see
                        # https://matplotlib.org/stable/users/explain/colors/colormaps.html
        )

        if self.hasToIncludeColorbar:    
            if not hasattr(self,'colorbar'):
                self.colorbar = plt.colorbar(self.contourfPlot,location='left')
                self.colorbar.ax.tick_params(labelsize=1000) #IH241114 this does not work
                # IH241114 WARNING The colorbar color scale is not updated, ie. it always persists as having been setup initially

                # IH241114 PROBLEM this issues the following warning:
                # UserWarning: Adding colorbar to a different Figure <Figure size 1000x20000 with 2 Axes>
                # than <Figure size 640x480 with 1 Axes> which fig.colorbar is called on.

        # show isolines
        if not self.hasToIncludeColorbar:
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
        if not self.hasToIncludeColorbar:
          self.scatterPlot = self.axes.scatter(
                        self.xScattered_Array,
                        self.yScattered_Array,
                        c='red',
                        s=10
          )
          pntIndex=0 
          for pntName in valuesDict:
            #IH 241114 this relies on the fixed order of keys in a dictionary
            self.axes.text(self.xScattered_Array[pntIndex]+0.5,self.yScattered_Array[pntIndex]-0.5,pntName,fontsize=8,color='red')
            pntIndex +=1

        # show additional graphics
        patches = []
        patches.append(Circle((0,0),30))
        patchCollection = PatchCollection(patches,alpha=0.5)
        self.axes.add_collection(patchCollection)

        # cosmetics
        self.axes.axis('equal')
        self.axes.set_axis_off()
        
        #IH241114 'text' used rather than 'title' to save space
        self.axes.text(0,-25.5,self.title,color='white',fontsize='x-small',horizontalalignment='center',verticalalignment='bottom')
        # self.axes.set_title(self.title,color='white')
        # self.axes.title.set_fontsize('x-small')
        
        

        self.draw()
       