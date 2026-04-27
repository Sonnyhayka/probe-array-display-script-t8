# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 10:34:29 2023

@author: Noah Haggerty

"""

from PyQt5.QtCore import QThread, pyqtSignal

class PlotThread(QThread):
    def __init__(self, io, **kwargs):
        super().__init__(**kwargs)
        self.io = io
        self.active = True
    
    sendData = pyqtSignal(dict)  
    
    def setActive(self, active):
        self.active = active
    
    def run(self):
        QThread.sleep(2) # lets reading start before plotting begins
        while self.active:
            data = self.io.getPlotData()
            QThread.msleep(100) # ~10 FPS
            self.sendData.emit(data)