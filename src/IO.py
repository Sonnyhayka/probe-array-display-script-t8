"RISE CONTROL CODE"

"Modified by L. Corson for use in the linear Langmuir probe array code for SupRISE"
"Modified, restructured by N.Haggerty for RISE"
"Based on code by J.Beckers and S.Bouwmans, modified by D.A.Klasing, for MACE"

import time
import numpy as np
import datetime
import IODevice as io
import Utils as u
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from DataManager import ControlDataManager

class IO(QObject): 
    """
    A class to handle all of the labjack and data logging for the probes.

    ...

    Attributes
    ----------
    terminate : bool
        Whether the currently-running control sequence should be terminated.
        (associated with the abort method)
    in_control_routine : bool
        Whether the IO is currently executing a control routine. Prevents multiple
        control routines from being executed simultaneously.
    reference_time : float
        When the IO was started in seconds since the epoch. Used to subtract from
        all time values.
    sendUpdate : PyQT Signal
        A signal used to update the message at the bottom of the GUI
    shotname : str
        The name of the data logging session
    settings_dict : dict
        Tracks the set points from the data logging session to be saved as the
        settings json
    data_manager : ControlDataManager
        Responsible for interfacing with and managing interaction the database.
    devices : List(Device)
        A list of all the input and output devices on the test stand
    lab_jack : LabJack
        Handles the LabJack device on the test stand    

    Methods
    -------
    update(str) : None
    getPlotData() : dict
    start_log(str) : bool
    stop_log() : None
    close() : None
    addSettings(dict) : None
    __saveSettings() : None
    checkShotDuplicate(str): bool
    updateResistance(int) : None
    getResistance() : int
    startProbeLogging(dict) : bool
    stopProbeLogging() : None
"""
    
    def __init__(self):
        super().__init__()
        self.in_control_routine = False
        self.reference_time = time.time()
            
        # Opening all of the stands devices
        # Add labJack ports here!! It'll be AUTOMATICALLY updated in
        # the rest of the code -- except adding graphs to the GUI in GUIdisplay
        # Make sure to add new devices to the self.devices list
        
        self.update("Opening LJM ports")
        self.lab_jack = io.LabJack("LAB_JACK", reference_time = self.reference_time)
        
        #AIN: Analog Input (computer input)
        self.lab_jack.addPort("LANG_VOL", "AIN0", _resolution=5, _range = 10)

# =============================================================================
#         Naming convention: LANG_CUR_a_b where a is a number referring to the probe number (1-5 where 1 is closest to the LEMO connector) and 
#         b is a number referring to which voltage measurement it is (1 means the voltage measurement closer to the probe and 2 means the 
#         voltage measurement after the resistor and farther from the probe)
# =============================================================================        
        self.lab_jack.addPort("LANG_CUR_3", "AIN1", _resolution=5, _range = 10)
        self.lab_jack.addPort("LANG_CUR_4", "AIN2", _resolution=5, _range = 10)
        self.lab_jack.addPort("LANG_CUR_1", "AIN3", _resolution=5, _range = 10)
        self.lab_jack.addPort("LANG_CUR_2", "AIN4", _resolution=5, _range = 10)
        self.lab_jack.addPort("LANG_CUR_5", "AIN5", _resolution=5, _range = 10)
        
        
        
        def curProcessing(input):
            
            voltage_processed = input #* 1.3 - 0.35
            current = voltage_processed / int(self.getResistance())
            
            return current
        
        self.lab_jack.addProcessingFunc("LANG_VOL", lambda vol: vol*10.417)
        self.lab_jack.addProcessingFunc("LANG_CUR_1", curProcessing)
        self.lab_jack.addProcessingFunc("LANG_CUR_2", curProcessing)
        self.lab_jack.addProcessingFunc("LANG_CUR_3", curProcessing)
        self.lab_jack.addProcessingFunc("LANG_CUR_4", curProcessing)
        self.lab_jack.addProcessingFunc("LANG_CUR_5", curProcessing)
    
        self.lab_jack.openDevice() # Doesn't do anything, but just to be thorough :)
        
        self.devices = [self.lab_jack]
        
    sendUpdate = pyqtSignal(str)
    
    def update(self, update_str, error = False):
        """Sends an update string to the GUI to be displayed at the bottom of the window."""
        if(error):
            print("[" + datetime.datetime.now().strftime('%H:%M:%S') + "]: ERROR-> " + update_str)
        else:
            print("[" + datetime.datetime.now().strftime('%H:%M:%S') + "]: " + update_str)
            
        self.sendUpdate.emit(update_str)
        
    def getPlotData(self):
        """Gets data from all of the devices in a dict format easy for GUIdisplay to plot."""
        plot_dict = {}
        for device in self.devices:
            plot_dict[device.getName()] = device.getPlotData()
        return plot_dict
    
    def checkShotDuplicate(self, shot_name):
        data_manager = ControlDataManager()
        return data_manager.checkDuplicateShot(shot_name)

    def start_log(self, shot_number = ""):
        """Starts logging for all devices and creates a ControlDataManager for the logging session. If log_name is None it creates a Shot, otherwise a Log. (Plasma vs no plasma, respectively.)"""
        self.settings_dict = {}
        data_manager = ControlDataManager()
        
        self.shotname = data_manager.createShot(shot_number)
        
        if self.shotname is None:
            self.update("Could not create shot directory.", error=True)
            return False
            
        for device in self.devices:
            device.startLogging(data_manager)
        
        self.data_manager = data_manager
        
        self.addSettings({"SHOT_NUMBER": self.shotname,"REFERENCE_TIME": self.reference_time, "LOG_START_TIME": time.time() - self.reference_time,
                         "TIME":datetime.datetime.now().strftime('%H:%M:%S'),  "DATE": datetime.date.today().strftime("%m/%d/%Y")})
        
        return True

    def start(self):
        """For starting the control code. Starts reading for all of the devices. This is required to start logging or display values on the GUI graphs."""
        for device in self.devices:
            device.startReading()

    def stop_log(self):
        """Stops logging for all devices, saves set points to the settings json."""
        for device in self.devices:
            device.stopLogging()
        try:
            self.addSettings({"LOG_END_TIME": time.time() - self.reference_time})
            self.addSettings({"LOG DURATION": self.settings_dict["LOG_END_TIME"] - self.settings_dict["LOG_START_TIME"]})
            self.__saveSettings()
        except:
            return
        
    def close(self, thread = True):
        """For closing control code. Stops device reading and closes the devices.""" 
        for device in self.devices:
            device.stopReading(thread)
            device.closeDevice()
        
    def addSettings(self, settings_dict):
        """Adds settings from a dict to be saved as set points in the settings json."""
        self.settings_dict.update(settings_dict)

        
    def __saveSettings(self):
        """Saves the stored settings from the settings_dict to the database."""
        self.data_manager.saveSettings(self.settings_dict)
        self.data_manager.writeXL(self.settings_dict)
        self.settings_dict = {}
    
        
    def updateResistance(self, resistance):
        self.lab_jack.updateResistance(resistance)
    
    def getResistance(self):
        return self.lab_jack.getResistance()

    
    def startProbeLogging(self, shot_data):
        """
        Turns on measuring for the langmuir probe array
        
        First, checks if the shot number was inputted. If it wasn't it starts logging with no inputted name, letting the program name it.
        If it was, it checks if the shot number is a duplicate or not.
        If it is a duplicate, it returns False to stop logging. If it isn't it starts logging with that name.
        """
        
        if shot_data["SHOT_NUMBER"] == "":
            if not self.start_log():
                return False
        else:
            if self.checkShotDuplicate(shot_data["SHOT_NUMBER"]):
                return False
            if not self.start_log(shot_data["SHOT_NUMBER"]):
                return False

        self.addSettings(
            {"RESISTANCE": shot_data["RESISTANCE"], "COMMENT": shot_data["COMMENT"]}
        )
        return True
    
    def stopProbeLogging(self):
        "Stops the probe logging."
        self.stop_log()