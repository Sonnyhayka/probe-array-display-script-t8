# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 08:21:03 2023

@author: Noah Haggerty

Modified by L. Corson for use in the linear Langmuir probe array code for SupRISE
"""

import sys
sys.path.insert(0, "..\\..")

from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import pyqtSlot
import pyqtgraph as pg
import numpy as np
from GUIthreads import PlotThread
from Utils import find

class MaceDisplay(QWidget):
    def __init__(self, io, **kwargs):
        super().__init__(**kwargs)
        pg.setConfigOption('foreground', 'w')
        self.grid = QGridLayout(self)
        self.setLayout(self.grid)
        
        self.view1 = pg.GraphicsView(self)
        self.layout1 = pg.GraphicsLayout()
        self.view1.setCentralWidget(self.layout1)
        
        self.view2 = pg.GraphicsView(self)
        #self.view2.setYRange((-1.1, 1.1))
        self.layout2 = pg.GraphicsLayout()
        self.view2.setCentralWidget(self.layout2)
        
        self.view3 = pg.GraphicsView(self)
        self.layout3 = pg.GraphicsLayout()
        self.view3.setCentralWidget(self.layout3)
        
        self.view4 = pg.GraphicsView(self)
        self.layout4 = pg.GraphicsLayout()
        self.view4.setCentralWidget(self.layout4)
        
        self.view5 = pg.GraphicsView(self)
        self.layout5 = pg.GraphicsLayout()
        self.view5.setCentralWidget(self.layout5)
        
        self.view6 = pg.GraphicsView(self)
        self.layout6 = pg.GraphicsLayout()
        self.view6.setCentralWidget(self.layout6)
        
        
        self.grid.addWidget(self.view1, 0, 0)
        self.grid.addWidget(self.view2, 0, 1)
        self.grid.addWidget(self.view3, 0, 2)
        self.grid.addWidget(self.view4, 1, 0)
        self.grid.addWidget(self.view5, 1, 1)
        self.grid.addWidget(self.view6, 1, 2)
        
        self.layout_list = [self.layout1, self.layout2, self.layout3, self.layout4, self.layout5, self.layout6]
        
        self.setMinimumHeight(600)
        self.setMinimumWidth(1000)
        
        self.plots = []
        self.plot_dict = {}
        self.io = io
        self.legends = []
        
        lang_cur_plot_all = MacePlotNum()
        lang_cur_plot_all.setScatter(True)
        lang_cur_plot_all.setLegend(True)
        self.legends.append(lang_cur_plot_all)
        added_plots = ["LANG_CUR_1", "LANG_CUR_2", "LANG_CUR_3", "LANG_CUR_4", "LANG_CUR_5"]
        lang_cur_plot_all.addLegendNames(added_plots)
        lang_cur_plot_all.setKeys("LAB_JACK", "LANG_VOL", added_plots)
        lang_cur_plot_all.setLabel("left", "Current", "A")
        lang_cur_plot_all.setLabel("bottom", "Applied Voltage", "V")
        lang_cur_plot_all.setTitle("LANGMUIR CURRENT")
        self.plot_dict["langmuir current all"] = lang_cur_plot_all
        
        lang_cur_plot1 = MacePlotNum()
        lang_cur_plot1.setScatter(True)
        lang_cur_plot1.setKeys("LAB_JACK", "LANG_VOL", "LANG_CUR_1")
        lang_cur_plot1.setLabel("left", "Current", "A")
        lang_cur_plot1.setLabel("bottom", "Applied Voltage", "V")
        lang_cur_plot1.setTitle("LANGMUIR CURRENT 1")
        self.plot_dict["langmuir current 1"] = lang_cur_plot1
        
        lang_cur_plot2 = MacePlotNum()
        lang_cur_plot2.setScatter(True)
        lang_cur_plot2.setKeys("LAB_JACK", "LANG_VOL", "LANG_CUR_2")
        lang_cur_plot2.setLabel("left", "Current", "A")
        lang_cur_plot2.setLabel("bottom", "Applied Voltage", "V")
        lang_cur_plot2.setTitle("LANGMUIR CURRENT 2")
        lang_cur_plot2.setColor(1)
        self.plot_dict["langmuir current 2"] = lang_cur_plot2
        
        lang_cur_plot3 = MacePlotNum()
        lang_cur_plot3.setScatter(True)
        lang_cur_plot3.setKeys("LAB_JACK", "LANG_VOL", "LANG_CUR_3")
        lang_cur_plot3.setLabel("left", "Current", "A")
        lang_cur_plot3.setLabel("bottom", "Applied Voltage", "V")
        lang_cur_plot3.setTitle("LANGMUIR CURRENT 3")
        lang_cur_plot3.setColor(2)
        self.plot_dict["langmuir current 3"] = lang_cur_plot3
        
        lang_cur_plot4 = MacePlotNum()
        lang_cur_plot4.setScatter(True)
        lang_cur_plot4.setKeys("LAB_JACK", "LANG_VOL", "LANG_CUR_4")
        lang_cur_plot4.setLabel("left", "Current", "A")
        lang_cur_plot4.setLabel("bottom", "Applied Voltage", "V")
        lang_cur_plot4.setTitle("LANGMUIR CURRENT 4")
        lang_cur_plot4.setColor(3)
        self.plot_dict["langmuir current 4"] = lang_cur_plot4
        
        lang_cur_plot5 = MacePlotNum()
        lang_cur_plot5.setScatter(True)
        lang_cur_plot5.setKeys("LAB_JACK", "LANG_VOL", "LANG_CUR_5")
        lang_cur_plot5.setLabel("left", "Current", "A")
        lang_cur_plot5.setLabel("bottom", "Applied Voltage", "V")
        lang_cur_plot5.setTitle("LANGMUIR CURRENT 5")
        lang_cur_plot5.setColor(4)
        self.plot_dict["langmuir current 5"] = lang_cur_plot5
        
        
        self.arrange_dict = {}
        self.arrange_dict["linear probe array"] = ["langmuir current all", "langmuir current 1", "langmuir current 2", "langmuir current 3", "langmuir current 4", "langmuir current 5"]
        
        self.plot_thread = PlotThread(self.io, parent = self)
        self.plot_thread.sendData.connect(self.updateData)
        self.plot_thread.start()
        
        self._addPlots() #While the old version of this code had more complicated machinery to show plots and switch between windows that seemed
                         #unnecessary here so this is pretty hard-coded
                
    def _clearPlots(self):
        #self.layout.clear()
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget is not None:
                self.grid.removeWidget(widget)
                widget.deleteLater()
        self.plots = []

    def _addPlots(self):
        for i in range(len(self.layout_list)):
            plot = self.plot_dict[self.arrange_dict["linear probe array"][i]]
            self.layout_list[i].addItem(plot, 0, 0)
            self.plots.append(plot)
    
    #may be used later by interactive GUI plot configuration
    def setPlotKeys(self, x_key, y_key, row, column):
        plot = self.layout.getItem(row, column)
        plot.setKeys(x_key, y_key)
     
    @pyqtSlot(dict)
    def updateData(self, mace_data):
        for plot in self.plots:
            plot.updateData(mace_data)
            
    @pyqtSlot()
    def clear(self):
        for plot in self.plots:
            plot.clear()
            
    def resizeEvent(self, event):
        "Checks for a resize event and updates the legend font size accordingly."
        for legend in self.legends:
            test_font_size = int(event.size().width() / 200) 
            if test_font_size < 12 and test_font_size > 6:
                new_font_size = test_font_size
            elif test_font_size <= 6:
                new_font_size = 6
            else:
                new_font_size = 12
            
            if new_font_size != legend.legend_font_size:
                legend.changeLegendFontSize(new_font_size)
        super().resizeEvent(event)

class MacePlot(pg.PlotItem):
    def __init__(self, stepMode = None, **kwargs):
        super().__init__(**kwargs)
        #self.data_select_method = "x delta" # "frequency scan" # TODO: two classes
        self.color_list = ['#00FFFF', '#CC00CC', '#FEF65B', '#79C257', '#BF94E4']
        self.plot_data = []
        self.x_keys = "None"
        self.y_keys = []
        self.point_sample_step = 1
        self.scatter = False
        self.stepMode = stepMode        
        
        self.legendNames = []
        self.hasLegend = False
        self.legend = pg.LegendItem(offset = (50, 10), labelTextSize = '7pt')
        self.legend.setBrush('k')
        self.legend_font_size = 7
        self.plot_list = []
        #self.enableAutoRange(axis = 'y', enable = False)
        #self.setYRange(-1.5, 1.5)
        
            
    def setColor(self, color, index = 0):
        if isinstance(color, int):
            color = self.color_list[color]
        
        if self.scatter:
            self.plot_data[index].setSymbolBrush(color)
            self.plot_data[index].setSymbolPen(color)
        else:
            self.plot_data[index].setPen(color)
        
    def clear(self):
        for plot in self.plot_data:
            plot.setData([], [])
        
    def setSampleStep(self, step):
        self.point_sample_step = step
        
    def _addData(self, x_data, y_data, index = 0):
        x_data = x_data[1::self.point_sample_step]
        y_data = y_data[1::self.point_sample_step]
        self.plot_data[index].setData(x_data, y_data)

    def setScatter(self, scatter_bool):
        self.scatter = scatter_bool
        
    def setKeys(self, device, x_keys, y_keys):
        self.device = device
        self.device2 = "dummy"
        self.x_keys = x_keys
        if isinstance(y_keys, str):
            self.y_keys = [y_keys]
        else:
            self.y_keys = y_keys 
        self.plot_list = []
        for i in range(0, len(self.y_keys)):
            if self.hasLegend is True and len(self.y_keys) == len(self.legendNames):
                self.legend.setParentItem(self)
                if self.scatter:
                    plot = self.plot([], [], symbol ='x', pen = None, symbolSize = 5, symbolBrush = self.color_list[i], symbolPen = self.color_list[i])
                    self.plot_list.append(plot)
                    self.plot_data.append(plot)
                    self.legend.addItem(plot, self.legendNames[i])
                else:
                    plot = self.plot([], [], stepMode = self.stepMode, pen = self.color_list[i])
                    self.plot_data.append(plot)
                    self.plot_list.append(plot)
                    self.legend.addItem(plot, self.legendNames[i])
            else:
                if self.hasLegend is True:
                    print("You must have a legend name for each curve. Plotting without legend.")
                if self.scatter:
                    plot = self.plot([], [], symbol ='x', pen = None, symbolSize = 5, symbolBrush = self.color_list[i], symbolPen = self.color_list[i])
                    self.plot_data.append(plot)
                    self.plot_list.append(plot)
                else:
                    plot = self.plot([], [], stepMode = self.stepMode, pen = self.color_list[i])
                    self.plot_data.append(plot)
                    self.plot_list.append(plot)
                
    def addLegendNames(self, names):
        self.legendNames = names
    
    def setLegend(self, legendBool):
        self.hasLegend = legendBool
    
    def changeLegendFontSize(self, font_size):
        "This function changes the legend font size based on input from the resize function."
        if self.scene() is not None:
            self.scene().removeItem(self.legend)
        labelSize = str(font_size) + "pt"
        self.legend = pg.LegendItem(offset = (70, 1), labelTextSize = labelSize)
        self.legend.setBrush('k')
        self.legend.setParentItem(self)
        
        for i in range(0, len(self.legendNames)):
            self.legend.addItem(self.plot_list[i], self.legendNames[i])
    
    def setKeys2dev(self, device1, device2, x_key, y_keys):
        self.device = device1
        self.x_keys = x_keys
        self.device2 = device2
        if isinstance(y_keys, str):
            self.y_keys = [y_keys]
        else:
            self.y_keys = y_keys 
        
        for i in range(0, len(self.y_keys)):
            if self.scatter:
                self.plot_data.append(self.plot([], [], symbol ='x', pen = None, symbolSize = 5, symbolBrush = self.color_list[i], symbolPen = self.color_list[i]))
            else:
                self.plot_data.append(self.plot([], [], stepMode = self.stepMode, pen = self.color_list[i]))    
    
    def updateData(self, mace_data):
        if self.device in mace_data.keys(): 
            oldx = mace_data[self.device][self.x_keys]
            if self.device2 != "dummy":
                for i in range(0, len(self.y_keys)):
                    #oldx = mace_data[self.device][self.x_key]
                    if np.isnan(oldx): 
                        newx = [0]
                        newy = [0]
                    else:
                        newx = [mace_data[self.device][self.x_keys]]
                        newy = [mace_data[self.device2][self.y_keys[i]][0]]
                    if self.x_keys in mace_data[self.device].keys() and self.y_keys[i] in mace_data[self.device2].keys():  
                        self._addData(newx, newy, i)
            else:
                for i in range(0, len(self.y_keys)):
                    if self.x_keys in mace_data[self.device].keys() and self.y_keys[i] in mace_data[self.device].keys():  
                        self._addData(mace_data[self.device][self.x_keys], mace_data[self.device][self.y_keys[i]], i)
       
class MacePlotNum(MacePlot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_points = 500
        self.point_sample_step = 10
    
    def _addData(self, x_data, y_data, index):  #TODO: add data None handling
        if len(x_data) > self.point_sample_step + 1: 
            x_data = x_data[1::self.point_sample_step]
            y_data = y_data[1::self.point_sample_step]
        new_data_len = len(x_data)
        data = self.plot_data[index].getData()
        if new_data_len >= self.num_points:
            self.plot_data[index].setData(x_data[-1-self.num_points:-1], y_data[-1-self.num_points:-1])
        elif new_data_len > 0 and data[0] is not None:
            old_to_keep = self.num_points - new_data_len
            new_x_data = np.append(data[0][-1-old_to_keep:-1], x_data)
            new_y_data = np.append(data[1][-1-old_to_keep:-1], y_data)
            self.plot_data[index].setData(new_x_data, new_y_data)
        else:
            self.plot_data[index].setData(x_data, y_data)
            
class MacePlotSubtract(MacePlot):
    """
    
    This class is still here in case the need to implement separate power supplies arises. This was designed to take two analog inputs
    and subtract them, only plotting one.
    
    """
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_points = 500
        self.point_sample_step = 10
        
    def updateData(self, mace_data):
        if self.device in mace_data.keys(): 
            #oldx = mace_data[self.device][self.x_keys]
            if isinstance(self.y_keys, list) and isinstance(self.y_keys[0], str):
                self.y_keys = [self.y_keys]
                
            

            for i in range(0, len(self.y_keys)):
                # if self.device2 != "dummy":
                #     if np.isnan(oldx): 
                #         newx = [0]
                #         newy = [0]
                #     else:
                #         newx = [mace_data[self.device][self.x_keys]]
                #         newy = [np.subtract(mace_data[self.device2][self.y_keys[i][0]][0], mace_data[self.device2][self.y_keys[i][1]][0])]
                #     if self.x_key in mace_data[self.device].keys() and self.y_keys[i][0] in mace_data[self.device2].keys() and self.y_keys[i][1] in mace_data[self.device2].keys():  
                #         self._addData(newx, newy, i)
                # else:
                    #print(mace_data)
                if len(self.x_keys) == 1:
                    if self.x_keys[0] in mace_data[self.device].keys() and self.y_keys[i][0] in mace_data[self.device].keys() and self.y_keys[i][1] in mace_data[self.device].keys():  
                        x_data = mace_data[self.device][self.x_keys[0]]
                        y_data = np.subtract(mace_data[self.device][self.y_keys[i][1]], mace_data[self.device][self.y_keys[i][0]])
                        self._addData(x_data, y_data, i)
                elif len(self.y_keys[i]) == 1:
                    if self.x_keys[0] in mace_data[self.device].keys() and self.x_keys[1] in mace_data[self.device].keys() and self.y_keys[i][0] in mace_data[self.device].keys():
                        x_data = np.subtract(mace_data[self.device][self.x_keys[1]], mace_data[self.device][self.x_keys[0]])
                        y_data = mace_data[self.device][self.y_keys[i][0]]
                        self._addData(x_data, y_data, i)
                elif self.x_keys[0] in mace_data[self.device].keys() and self.x_keys[1] in mace_data[self.device].keys() and self.y_keys[i][0] in mace_data[self.device].keys() and self.y_keys[i][1] in mace_data[self.device].keys():
                    x_data = np.subtract(mace_data[self.device][self.x_keys[1]], mace_data[self.device][self.x_keys[0]])
                    y_data = np.subtract(mace_data[self.device][self.y_keys[i][1]], mace_data[self.device][self.y_keys[i][0]])
                    self._addData(x_data, y_data, i)
               
                    
    
    def _addData(self, x_data, y_data, index = 0):  #TODO: add data None handling   
        if len(x_data) > self.point_sample_step + 1: 
            x_data = x_data[1::self.point_sample_step]
            y_data = y_data[1::self.point_sample_step]
        new_data_len = len(x_data)
        data = self.plot_data[index].getData()
        if new_data_len >= self.num_points:
            self.plot_data[index].setData(x_data[-1-self.num_points:-1], y_data[-1-self.num_points:-1])
        elif new_data_len > 0 and data[0] is not None:
            old_to_keep = self.num_points - new_data_len
            new_x_data = np.append(data[0][-1-old_to_keep:-1], x_data)
            new_y_data = np.append(data[1][-1-old_to_keep:-1], y_data)
            self.plot_data[index].setData(new_x_data, new_y_data)
        else:
            self.plot_data[index].setData(x_data, y_data)
            