#!/usr/bin/env python
# coding=utf-8
#

#-------------------------------------------------------------------------------
#
#   The Magnetic Resonance Scanner Mockup Project
#
#
#      M  R  S  M  _  S  t  y  l  e  s  h  e  e  t  .  p  y 
#
9
#      Last update: IH240909
#-------------------------------------------------------------------------------

# for examples, see
# https://github.com/Axel-Erfurt/Python-QT-VideoPlayer/blob/master/QT6_VideoPlayer.py
# https://doc.qt.io/qtforpython-6/overviews/stylesheet-examples.html

# for a guide on colors, see
# https://doc.qt.io/qtforpython-5/PySide2/QtGui/QColor.html

def MRSM_Stylesheet():
    return """
QWidget 
{ 
    background-color: darkCyan; /* this is the general bg color */
}

QPushButton 
{ 
    background-color: yellow;
    border: 2px;
    border-style: outset;
    border-radius:  25px;
    border-color: black;
    min-width:  20px;
    max-width:  100px;
    min-height:  50px;
}

QPushButton:disabled
{ 
    background-color: DarkGoldenRod;
}

QPushButton#bSagittal:enabled,
QPushButton#bCoronal:enabled,
QPushButton#bTransversal:enabled
{ 
    background-color: yellow;
}

QPushButton#bSagittal:disabled,
QPushButton#bCoronal:disabled,
QPushButton#bTransversal:disabled
{ 
    color: yellow;
    font-weight: bold;
    background-color: green;
}


QLabel#lCountdown, 
QLabel#lVersion  
{        
    font: bold 14px;
}

QLabel#lHTMLText1
{        
    font-size: 44px;    /* IH240729 this does not work with HTML rich-text contents */
}


#imagePaneRightmost
{
    background-color: cyan;
}

QLabel#lTitle 
{        
    font: bold 65px;    /* IH240729 65px is ok for RPI */
}

QLabel#lIdleTitleBig 
{        
    font: bold 60px;
    background-color: none;
}

QLabel#lIdleTitleSmall 
{        
    font: bold 30px;
    background-color: none;
}

QLabel#lRollerShadePaneLeft,
QLabel#lRollerShadePaneMid,
QLabel#lRollerShadePaneRight
{        
    background-color: darkCyan;
    /* background-color: black; */ 
}
    """
