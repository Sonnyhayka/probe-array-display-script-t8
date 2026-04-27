# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 08:21:18 2023

@author: Noah Haggerty

Modified by L. Corson for use in the linear Langmuir probe array code for SupRISE
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox, QLabel, QCheckBox, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt

class MaceControl(QWidget):
    def __init__(self, io, **kwargs): 
        super().__init__(**kwargs)
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.io = io
        
        self.control_dict = {
                            "Linear probe array": ProbeArrayWidget(io, parent = self)
                             }
        
        self.control_names = []
        for key in self.control_dict.keys():
            self.control_names.append(key)
            self.grid.addWidget(self.control_dict[key], 1, 0) # TODO: "stacked" widget
            self.control_dict[key].hide()
        
        self.current_key = self.control_names[0]
        
        self.control_combo = QComboBox(self)
        self.control_combo.addItems(self.control_names)
      
        self.grid.addWidget(self.control_combo, 0, 0)

        
        self.grid.addWidget(QWidget(), 2, 0) #spacer at the bottom to prevent excessive stretching
        self.grid.setRowStretch(2, 1)
        
        self.control_widget = QWidget(self)
        
        self.implementControlWidget(self.control_names[0])

        self.control_combo.currentTextChanged.connect(self.implementControlWidget)
        
        self.setMaximumWidth(350)
        
    updateDisplay = pyqtSignal(str)
    
    @pyqtSlot(str)    
    def implementControlWidget(self, key):
        self.control_dict[self.current_key].hide()
        self.control_dict[key].show()
        display_name = self.control_dict[key].getDisplayName()
        self.updateDisplay.emit(display_name)
        self.current_key = key


class ProbeArrayWidget(QWidget):
    def __init__(self, io, **kwargs):
        super().__init__(**kwargs)
        self.io = io
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.resistance = 50
        self.__logging = False
        
        self.resistance_line_edit = QLineEdit(self)
        self.shot_number_line_edit = QLineEdit(self)
        self.resistance_button = QPushButton("Change resistance", self)
        self.logging_button = QPushButton("Start logging", self)
        self.comment_line_edit = QLineEdit(self)
        self.resistance_text = QLabel("Resistance in use: " + str(self.io.getResistance()) + "ohms")
        
        self.grid.addWidget(QLabel("Resistance (ohms)", self), 0, 0)
        self.grid.addWidget(self.resistance_line_edit, 1, 0)
        self.grid.addWidget(self.resistance_button, 2, 0)
        self.grid.addWidget(self.resistance_text, 3, 0)
        self.grid.addWidget(QLabel("Shot number", self), 4, 0)
        self.grid.addWidget(self.shot_number_line_edit, 5, 0)
        self.grid.addWidget(QLabel("Comment", self), 6, 0)
        self.grid.addWidget(self.comment_line_edit, 7, 0)
        self.grid.addWidget(self.logging_button, 8, 0)
        
        self.logging_button.clicked.connect(self.changeLoggingState)
        self.resistance_button.clicked.connect(self.changeResistance)
        
    def getDisplayName(self):
        return "linear probe array"
        
    def changeResistance(self):
        self.io.updateResistance(self.resistance_line_edit.text())
        self.resistance = self.resistance_line_edit.text()
        self.resistance_text.setText("Resistance in use: " + str(self.io.getResistance()) + "ohms")
    
    def changeLoggingState(self):
        if self.__logging:
            self.io.stopProbeLogging()
            self.logging_button.setText("Start logging")
            self.__logging = False
        else:
            if self.resistance_line_edit.text() != '':
                self.resistance = self.resistance_line_edit.text()
                self.io.updateResistance(self.resistance)
            else:
                print("No resistance entered. Using the last entered resistance of " + str(self.resistance) + ".")
            shot_data = {'RESISTANCE':self.resistance, 'COMMENT' : self.comment_line_edit.text(), 'SHOT_NUMBER': self.shot_number_line_edit.text()}
            success = self.io.startProbeLogging(shot_data)
            
            if success:
                self.__logging = True
                self.logging_button.setText("Stop logging")