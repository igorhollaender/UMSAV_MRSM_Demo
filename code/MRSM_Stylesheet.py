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
#
#      Last update: IH240723
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
    """
