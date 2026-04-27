"SupRISE Linear Langmuir Probe CONTROL CODE"

"Modified again by L. Corson for the Linear Langmuir Probe Array on SupRISE"
"Modified, restructured by N.Haggerty for RISE"
"Based on code by J.Beckers and S.Bouwmans, modified by D.A.Klasing, for MACE"

import time
import pyvisa as visa
from LJ_DAQ import LJMport
from labjack import ljm
import numpy as np
import seabreeze.spectrometers as sb
import threading
#import u3
from Utils import extractNums
from datetime import datetime

class Device:
    """
    A class that represents a device on the test stand: an input device
    streaming sensor data to the control code and/or an output deivce sending
    commands from the control code to the test stand. The device subclasses
    act as wrappers to handle all of the complex (and annoying) communication
    protocol for the physical devices. 

    ...

    Attributes
    ----------
    ok: bool
        If the device is responsive, streaming data/able to receive commands
    _name : str
        The name of the device. Used in logging and sending plot data
    _reference_time : float
        Time in seconds since the "epoch" to use as a reference time to
        subtract from all time measurements
    logging : bool
        If the device is actively logging data into the database
    _log : nd.array
        cached log values. Dumped into the database after reaches a certain size.
        Used for performance reasons (computational cost of dumping values into
        database can be high).
    __dict_processing : dict
        Keys are the names of streamed data columns, values are lambda functions
        to processes the streamed data with, takes in a dictionary of the
        streamed data and returns an nd.array of floats representing the processed
        values for the column of the key (dict processing instead of float processing
        means that the processing function for one column is dependent on another
        -- for example, the Langmuir current calibration is dependent on what
        the Langmuir voltage is).
    __float_processing : dict
        Keys are the names of streamed data columns, values are lambda functions
        to process the streamed data with, takes in an nd.array of floats,
        representing the raw data for the data column of the key, and returns
        an nd.array of floats, representing the processed data for the data
        column of the key
    _log_names : list(str)
        List of all the data column names streamed with the device and logged
        into the database

    Methods
    -------
    getName() : str
    _processingFunc(nd.array) : nd.array
    addProcessingFunc(str, func, bool) : None
    getProcessingFunc(str): func
    _updateLog(nd.array) : nd.array
    addLogNames(list(str)) : None
    updateReferenceTime(float) : None
    hasLogName(str) : bool
    isOk() : bool
    getPlotData() : dict
    startLogging(ControlDataManager) : None
    stopLogging() : None
    startReading() : None
    stopReading() : None
    openDevice() : None
    closeDevice() : None
    """
    
    def __init__(self, name, reference_time = 0):
        """
        Parameters:
            name (str): name of the device. used for logging and sending plot data
            reference_time (float): time in seconds from the epoch to subtract
                from all time values
        """
        self.ok = False
        self._name = name
        self.logging = False
        self._reference_time = reference_time
        self.__dict_processing = {}
        self.__float_processing = {}
        
        self._log_names = ["TIME"] # All devices track the time that data is transfered between the test stand and control code/database
        self.addProcessingFunc("TIME", lambda time: time - self._reference_time)
     
    def getName(self):
        """Returns the name of the device."""
        return self._name
    
    def console_out(self, msg, error=False):
        if(error):
            print("[" + datetime.now().strftime('%H:%M:%S') + "]: ERROR-> " + msg)
        else:
            print("[" + datetime.now().strftime('%H:%M:%S') + "]: " + msg)
    
    def _processingFunc(self, data):
        """
        Uses the processing functions defined with addProcessingFunc (then stored
        in self.__dict_processing and self.__float_processing) to process the
        data passed in.
        
        Parameters:
            data (nd.array): 2D array of the streamed data. columns must line up
            with self._log_names
            
        Returns:
            nd.array: processed data, of same dimensions as argument
        """
        if not isinstance(data, dict):
            if len(data) == 0:
                return data
            data_dict = {}
            for i in range(0, len(data[0,:])):
                data_dict[self._log_names[i]] = data[:,i]
        else:
            data_dict = data
            
        for key in self.__float_processing:
            if key in data_dict:
                data_dict[key] = self.__float_processing[key](data_dict[key])
            
        for key in self.__dict_processing:
            if key in data_dict:
                data_dict[key] = self.__dict_processing[key](data_dict)
        
        if not isinstance(data, dict):
            for i in range(0, len(data[0,:])):
                data[:,i] = data_dict[self._log_names[i]]
        else:
            data = data_dict
            
        return data
        
    def addProcessingFunc(self, key, func, dict_arg = False):
        """
        Adds a processing func to be used on streamed data.
        
        Parameters:
            key (str): name of the streamed data column the processing function
                should be applied to
            func (func(nd.array): nd.array/func(dict): nd.array): processing
                function. EITHER takes in a 1D nd.array of data values corresponding with
                key and returning processed 1D nd.array OR takes in a dictionary with
                all of the log names as keys and 1D nd.arrays of streamed data as values
                and returning processed 1D np.array corresponding with key
            dict_arg (bool): If the func takes in a dictionary as the argument
                (as opposed to a 1D nd.array)
                
        Returns:
            None.
        """
        if dict_arg:
            self.__dict_processing[key] = func
        else:
            self.__float_processing[key] = func
            
    def getProcessingFunc(self, log_name):
        """Returns the processing function for the given log name."""
        if log_name in self.__float_processing:
            return self.__float_processing[log_name]
        elif log_name in self.__dict_processing:
            return self.__dict_processing[log_name]
        else:
            raise KeyError("No processing func for key " + log_name + " was found.")
        
    def startLogging(self, data_manager):
        """Starts logging and sets the ControlDataManager for the device."""
        self.logging = True
        self.data_manager = data_manager
        self._log = np.zeros((0,len(self._log_names)))
    
    def stopLogging(self):
        """Stops logging, saves final batch of data, for the device."""
        try:
            if self.isOk():
                self.logging = False
                self.data_manager.saveData(self.getName(), self.getType(), self._processingFunc(self._log))
                self._log = np.zeros((0,len(self._log_names)))
        except:
            self.logging = False

    def _updateLog(self, data):
        """Adds data to the database, updates data cache in the class."""
        pass
    
    def startReading(self):
        """Starts data reading for the device: data is streamed to control code but not saved in database."""
        pass
    
    def stopReading(self):
        """Stops reading for the device: data no longer streamed to control code."""
        pass
        
    def isOk(self):
        """Returns if the device is ok, still connected, talking, and able to stream."""
        return self.ok
    
    def openDevice(self):
        """Opens a connection to the device."""
        pass
    
    def closeDevice(self):
        """Properly closed the connection to the device."""
        pass
    
    def getPlotData(self):
        """returns a dictionary with the most recent data streamed, for plotting in the GUI."""
        pass
    
    def addLogNames(self, names):
        """Adds more log names to the device. Log names are  a list of all the data column names streamed with the device and logged into the database."""
        self._log_names = self._log_names + names
    
    def updateReferenceTime(self, time):
        """Updates the reference time of the device. Reference time is a time in seconds since the "epoch" to use as a reference time to subtract from all time measurements."""
        self._reference_time = time
        self.addProcessingFunc("TIME", lambda time: time - self._reference_time)
        
    def hasLogName(self, name):
        """Returns if the device has the given log name. Log names are  a list of all the data column names streamed with the device and logged into the database."""
        return name in self._log_names
    
    
class ODevice(Device):
    """
    A class that represents an output device on the test stand: a device that
    sends commands from the control code to the test stand. Logs values into 
    the database as they're set. The device subclasses
    act as wrappers to handle all of the complex (and annoying) communication
    protocol for the physical devices. 

    ...
    ALL OF THE ATTRIBUTES AND METHODS OF Device AND ...

    Attributes
    ----------
    _current_vals : dict
        holds all the log names and their most recent set values. This is used
        for plotting and logging.

    Methods
    -------
    send(Any) : None
    getType() : str

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_vals = None
        
    def send(self, command):
        pass
    
    def getType(self):
        """Returns the class of device; in this case, output."""
        return "OUTPUT"
    
    def _updateLog(self, data_dict):
        """
        Parameters:
            data_dict (dict): log names with updated values. Any possible log
                name set value not in the dict is assumed to be the same as
                prior to the current _updateLog call
        """
        data_dict["TIME"] = time.time()
        new_row = []
        
        for name in self._log_names:
            if name in data_dict.keys():
                new_row.append(data_dict[name])
                self._current_vals[name] = data_dict[name]
            else:
                new_row.append(self._current_vals[name])
        
        if self.logging:
            self._log = np.append(self._log, np.array([np.array(new_row)]), axis = 0)
    
    def startReading(self):
        if self._current_vals is None:
            self._current_vals = {}
            for name in self._log_names:
                self._current_vals[name] = np.nan
        
    def getPlotData(self):
        if self.isOk():
            new_dict = {}
            for key in self._current_vals.keys():
                new_dict[key] = np.array([self._current_vals[key]])
            
            # Updates the time each time the GUI calls to update the plots. Input data
            # streams are generally faster than the GUI can update the plots, meaning
            # they can use their real time and look smooth. Since output devices might only set values
            # only every handful of seconds, to create smooth motion of graph, needs
            # to reupdate the time with the same set values instead of waiting for
            # new vales to be set.
            new_dict["PLOT_TIME"] = np.array([time.time() - self._reference_time])
            
            return self._processingFunc(new_dict)
        else:
            return {}
        
    def startLogging(self, data_manager):
        super().startLogging(data_manager)
        self.data_manager.addDevice(self.getName(), self.getType(), self._log_names)
                
 
class IDevice(Device):
    """
    A class that represents an input device on the test stand: streams data from
    sensors from the test stand to the control code and logs into the database.
    The device subclasses act as wrappers to handle all of the complex
    (and annoying) communication protocol for the physical devices. 

    ...
    ALL OF THE ATTRIBUTES AND METHODS OF Device AND ...

    Attributes
    ----------
    _temp_log : nd.array
        short cache of recent values to be referenced for plotting
    _temp_store_max : int
        number of values to save for each log name in _temp_log
    _log_store_max_tot : int
        total number of vals (sum of vals stored for each column) in _log before
        dumping the data into the database
    __temp_len : int
        current length of each log name column in _temp_log
    __log_len : int
        current length of each log name column in _log

    Methods
    -------
    getType() : str

    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._temp_store_max = 500
        self._log_store_max_tot = 50000
        self.__temp_len = 0
        self.__log_len = 0
        
            
    def getType(self):
        """Returns the class of device; in this case, input."""
        return "INPUT"
    
    def startReading(self):
        super().startReading()
        self._temp_log = np.zeros((0,len(self._log_names)))
    
    def getPlotData(self):
        if self.isOk():
            plot_dict = {}
            for i in range(0,len(self._log_names)):
                plot_dict[self._log_names[i]] = self._temp_log[:,i]
            return self._processingFunc(plot_dict)
        else:
            return {}
    
    def _updateLog(self, data):
        if self.isOk():
            # add data to temp log
            self.__temp_len += len(data[:,0])
            self._temp_log = np.append(self._temp_log, data, axis = 0)
            
            # cut down temp log to max temp log length if over
            if self.__temp_len > self._temp_store_max:
                self._temp_log = self._temp_log[self.__temp_len-self._temp_store_max:self.__temp_len,:]
                self.__temp_len = self._temp_store_max
            
            # if logging to database ...
            if self.logging:
                # add data to log
                self.__log_len += len(data[:,0])
                self._log = np.append(self._log, data, axis = 0)
                
                # if log length is over max log length, save to database, clear cached log
                if self.__log_len > self._log_store_max:
                    self.data_manager.saveData(self.getName(), self.getType(), self._processingFunc(self._log))
                    self._log = np.zeros((0,len(self._log_names)))
                    self.__log_len = 0
      
    def startLogging(self, data_manager):
        print("started logging")
        self._log_store_max = int(self._log_store_max_tot / len(self._log_names))
        super().startLogging(data_manager)
        self.data_manager.addDevice(self.getName(), self.getType(), self._log_names)

class IODevice:
    """
    A class that represents an input output device on the test stand: both
    streaming sensor data to the control code (input) and sending commands
    from the control code to the test stand (output). The device subclasses
    act as wrappers to handle all of the complex (and annoying) communication
    protocol for the physical devices. 
    
    Attributes
    ----------
    ok: bool
        If the device is responsive, streaming data/able to receive commands
    _name : str
        The name of the device. Used in logging and sending plot data
    logging : bool
        If the device is actively logging data into the database
    _i_device : IDevice
        Handles the input logging/plot functionality of the device
    _o_device : ODevice
        Handles the output logging/plot functionality of the device
    
    
    Methods
    -------
    getName() : str
    addProcessingFunc(str, func, bool) : None
    getProcessingFunc(str): func
    updateReferenceTime(float) : None
    isOk() : bool
    getPlotData() : dict
    startLogging(ControlDataManager) : None
    stopLogging() : None
    startReading() : None
    stopReading() : None
    openDevice() : None
    closeDevice() : None       
    """
    
    def __init__(self, name, reference_time = 0):
        """
        Parameters:
            name (str): name of the device. used for logging and sending plot data
            reference_time (float): time in seconds from the epoch to subtract
                from all time values
        """
        self.ok = False
        self._name = name
        self.logging = False
        self._i_device = IDevice(name, reference_time)
        self._o_device = ODevice(name, reference_time)
        self._i_device.ok = True
        self._o_device.ok = True
        
    def console_out(self, msg, error=False):
        if(error):
            print("[" + datetime.now().strftime('%H:%M:%S') + "]: ERROR-> " + msg)
        else:
            print("[" + datetime.now().strftime('%H:%M:%S') + "]: " + msg)
    
    def getName(self):
        return self._name
    
    def isOk(self):
        return self.ok and self._i_device.isOk() and self._o_device.isOk()
    
    def send(self, command):
        pass
    
    def addProcessingFunc(self, key, func, dict_arg = False):
        if self._i_device.hasLogName(key):
            self._i_device.addProcessingFunc(key, func, dict_arg)
        elif self._o_device.hasLogName(key):
            self._o_device.addProcessingFunc(key, func, dict_arg)
            
    def getProcessingFunc(self, key):
        if self._i_device.hasLogName(key):
            return self._i_device.getProcessingFunc(key)
        if self._o_device.hasLogName(key):
            return self._o_device.getProcessingFunc(key)
        else:
            raise KeyError("No processing func for key " + key + " was found.")
            
    def getPlotData(self):
        if self.isOk():
            data = self._o_device.getPlotData() # TODO: messy, i_device needs to write over "TIME"
            data.update(self._i_device.getPlotData())
            return data
    
    def updateReferenceTime(self, time):
        self._i_device.updateReferenceTime(time)
        self._o_device.updateReferenceTime(time)
    
    def startLogging(self, data_manager):
        self.logging = True
        self._i_device.startLogging(data_manager)
        self._o_device.startLogging(data_manager)
        
    def stopLogging(self):
        self.logging = False
        self._i_device.stopLogging()
        self._o_device.stopLogging()
                
    def startReading(self):
        self._i_device.startReading()
        self._o_device.startReading()
        
    def stopReading(self):
        pass
    
    def openDevice(self):
        pass
    
    def closeDevice(self):
        pass
                
        
class LabJack(IODevice):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ports = {}
        self.i_ports = [] #TODO: get rid of 
        self.resistance = 50
    
    def updateResistance(self, resistance):
        self.resistance = resistance
        
    def getResistance(self):
        return self.resistance
    
    def isOk(self):
        return all([self.ports[key][0] for key in self.ports.keys()])
        
    def addPort(self, name, port, _range = -1, _resolution = -1):
        try:
            lab_jack_port = LJMport(port, _range=_range, _res=_resolution)
            self.ports[name] = (True, lab_jack_port)

        except:
            self.ports[name] = (False, None)
            self.console_out(name + " from " + self._name + " could not be found.", error=True)
        
        if port[0:3] == "AIN": # TODO: beter determination if in or out
            self.i_ports.append(port)
            self._i_device.addLogNames([name])
        else:
            self._o_device.addLogNames([name])
            
    def send(self, name, command):
        if(self.ports[name][0]):
            data_dict = {name: float(command)}
            self._o_device._updateLog(data_dict)
            self.ports[name][1].write(float(command))
        else:
            self.console_out(name + " cannot recieve commands because opening was unsuccessful.")
        
    def startReading(self):
        super().startReading()
        if self.isOk():
            self.device = ljm.openS("T8", "USB", "480010850")
            
            LJMport.set('STREAM_BUFFER_SIZE_BYTES', 262144)
            
            self.stream_length = 100
            self.stream_rate = 100
    
            LJMport.set('STREAM_RESOLUTION_INDEX', 0)
            LJMport.set('STREAM_SETTLING_US', 0)

            ljm.eStreamStart(self.device,
                             self.stream_length,
                             len(self.i_ports),
                             [ljm.nameToAddress(port)[0] for port in self.i_ports],
                             self.stream_length*self.stream_rate)        
            self.thread = threading.Thread(target=self.__threadFunc, daemon=True)   
            self.thread.start()
        
    def __threadFunc(self):
        current_thread = threading.currentThread()

        while(getattr(current_thread, "active", True)):
            def read_data():
                try:
                    return np.array(ljm.eStreamRead(self.device)[0]).reshape(self.stream_length, len(self.i_ports))
                except:
                    self.console_out("Buffer full, restarting stream")
                    ljm.eStreamStop(self.device)
                    ljm.eStreamStart(self.device,
                                     self.stream_length,
                                     len(self.i_ports),
                                     [ljm.nameToAddress(port)[0] for port in self.i_ports],
                                     self.stream_length*self.stream_rate)        
                    return np.array(ljm.eStreamRead(self.device)[0]).reshape(self.stream_length, len(self.i_ports))
                
            data = read_data()
            data_len = len(data[:,0])
            times = np.ones((data_len,1))*time.time()
            data = np.append(times, data, axis=1)

            self._i_device._updateLog(data)
            
    def stopReading(self, thread = True):
        if self.isOk() and thread:
            self.thread.active = False # TODO: cleaner way to do this?   
            ljm.eStreamStop(self.device)
        else:
            ljm.eStreamStop(self.device)
        
    def closeDevice(self):
        if self.isOk():
            ljm.closeAll()