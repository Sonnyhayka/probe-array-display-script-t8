# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 08:08:44 2023

@author: Noah Haggerty

Modified by L. Corson for use in the linear Langmuir probe array code for SupRISE
"""

from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget
from PyQt5.QtCore import pyqtSlot
from GUIdisplay import MaceDisplay
from GUIcontrol import MaceControl
from IO import IO

class MaceGui(QApplication):
    def __init__(self, *args):
        super().__init__(*args)
        window = MainWindow()
        window.show()
        self.exec_() # enter event loop
    
    
class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wrapper_widget = QWidget()
        self.grid = QGridLayout()
        self.wrapper_widget.setLayout(self.grid)
        self.setCentralWidget(self.wrapper_widget)
        self.setWindowTitle("SupRISE GUI")
        
        self.io = IO()
        self.io.start()
        
        self.display = MaceDisplay(self.io, parent=self)
        self.control = MaceControl(self.io, parent=self)
        
        self.grid.addWidget(self.control, 0, 0)
        self.grid.addWidget(self.display, 0, 1)
        
        self.bar = self.menuBar()
        self.bar.addMenu("Devices") 
        
        self.status = self.statusBar()
        self.io.sendUpdate.connect(self.status.showMessage)        
        
    def closeEvent(self, event):
        self.display.plot_thread.setActive(False) # TODO: gross handling
        self.io.close()
    
    @pyqtSlot()
    def resetDevices(self):
        self.io.close()
        
        self.io = IO()
        self.io.start()
        
        self.display.clear()