# -*- coding: utf-8 -*-
"supRISE DATABASE MANAGMENT CODE"

"Written by N. Haggerty, modified by K. van Lakwijk"
"Modified by L. Corson for use in the linear Langmuir probe array code for SupRISE"

import numpy as np
import os
import pickle as p
import pandas as pd
import csv
import ujson as json
import openpyxl 

class ControlDataManager:
    """
    A class to used by control code to manage database interactions for data
    logging.

    ...

    Attributes
    ----------
    _session_dir : str
        the directory data is read from and saved to

    Methods
    -------
    createShot() : None
    createLog(str) : None
    addDevice(str, str, list(str)) : None
    saveData(str, str, nd.array) : None
    saveSettings(dict) : None
    writeXL(dict) : None
    generateShotName(str) : str
    generateSessionDir(str) : str
    checkDuplicateShot(str) : bool
    """
    
    def __init__(self):
        self.data_filepath = "C:\\Users\\NeutralBeams2\\Documents\\MACE EXPERIMENT\\CODE\\Probe_Array_Display_Script_T8\\Data\\SHOT_DATA\\"
        self.XL_filepath = "C:\\Users\\NeutralBeams2\\Documents\\MACE EXPERIMENT\\CODE\\Probe_Array_Display_Script_T8\\Data\\"
       

    def writeXL(self,setting_data):
        # Check if the Excel file exists, if not, create a new one
        try:
            workbook = openpyxl.load_workbook(self.XL_filepath + 'supRISEshots.xlsx')
        except FileNotFoundError:
            workbook = openpyxl.Workbook()
        
        excel_administration_list = ["SHOT_NUMBER", "DATE", "TIME", "COMMENT"]
        excel_data_list = ["RESISTANCE", "LOG DURATION", "LOG_START_TIME", "LOG_END_TIME"]
        
        # Select the active sheet in the workbook
        if "Shots" not in workbook.sheetnames:
            sheet_title = workbook.sheetnames[0]
            workbook[sheet_title].title = "Shots"
            sheet = workbook["Shots"]
            
            column = 1
            for val in excel_administration_list:
                sheet.cell(row = 1, column = column, value = val)
                column += 1
                
            for val in excel_data_list:
                sheet.cell(row = 1, column = column, value = val)
                column += 1
                
        else:
            sheet = workbook["Shots"]          
            
        # Find the next available row in the sheet
        next_row = sheet.max_row + 1   
        end_col_letter = openpyxl.utils.get_column_letter(sheet.max_column)
        
        if "ShotData" not in sheet._tables:
            print(openpyxl.worksheet.table.Table(displayName = "ShotData", ref = f"A1:{end_col_letter}{next_row}"))
            sheet.add_table(openpyxl.worksheet.table.Table(displayName = "ShotData", ref = f"A1:{end_col_letter}{next_row}"))
        table = sheet._tables["ShotData"]
           

        for col,key in enumerate(excel_administration_list, start=1):

            sheet.cell(row=next_row, column=col, value=setting_data[key])
        
        for col,key in enumerate(excel_data_list, start=len(excel_administration_list)+1):
            if key in setting_data:
                sheet.cell(row=next_row, column=col, value=setting_data[key])
       
        start_cell = table.ref.split(":")[0]
        end_col_letter = openpyxl.utils.get_column_letter(sheet.max_column)
        table.ref = f"{start_cell}:{end_col_letter}{next_row}"

        '''
        # Write the values from the dictionary to the next row
        values = list(setting_data.values())
        for col, value in enumerate(values, start=1):
            sheet.cell(row=next_row, column=col, value=value)
        '''
        # Save the workbook
        workbook.save(self.XL_filepath + 'supRISEshots.xlsx')

        # Close the workbook
        workbook.close()

    def addComment(self, shotname, text):
        file_path = self.XL_filepath + 'supRISEshots.xlsx'
        sheet_name = "Shots"
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook[sheet_name]
        rows = sheet.iter_rows()
        shot_found = False
        for row in rows:  # Skip header row
            if row[0].value == shotname:
                row[4].value = text  
                shot_found = True
                break
        workbook.save(file_path)
        return shot_found
    
    def generateShotName(self, shot_name = "", check_duplicate = False):
        """
        Takes a number inputted by the user and adds the appropriate number of 0s in front to make it 5 digits (if it isn't already)
        If the input is a string of length 0, this function will check if there are other numbered shots in the correct directory.
        If there are, the shot name is one higher than the highest shot number. If there aren't the shot name is 00001.
        
        """
        
        try: 
            dirs = os.listdir(self.data_filepath)
            if len(shot_name) > 0:
                if len(shot_name) < 5:
                    for i in range(0, 5-len(shot_name)):
                        shot_name = "0" + shot_name
                session_name = shot_name
            elif len(dirs) == 0: # if shot directory empty, shot number is 1
                session_name = "00001"
            elif check_duplicate is False: # set shot name to one above the highest shot number in the directory
                rows = []
                for i in np.arange(0, len(dirs)):
                    rows.append(int(dirs[i]))
                session_name = "{:05d}".format(max(rows)+1)
            else:
                return ""
            return session_name
        except:
            return None
    
    def generateSessionDir(self, shot_name = ""):
        "Generates a directory path for a given shot number"
        if len(shot_name) < 5:
            session_name = self.generateShotName(shot_name)
        else:
            session_name = shot_name
        session_dir = self.data_filepath + session_name + "\\"
        
        return session_dir
    
    def checkDuplicateShot(self, shot_name):
        "Checks if a given shot directory already exists in order to check if the user inputted a duplicate shot number."
        "Returns True for a duplicate."
        
        session_dir = self.generateSessionDir(shot_name)
        
        if(os.path.isdir(session_dir)):
            print("The shot number you entered already exists. Please enter a different number.")
            return True
        else:
            return False
    
    def createShot(self, shot_name = ""):
        """
        Creates shot directory to save data to, returns shot name

        Returns:
            session_name (str): number of the shot, empty string if creating directory failed
        """
        session_name = self.generateShotName(shot_name)
        self._session_dir = self.generateSessionDir(shot_name = session_name)
        
        if(os.path.isdir(self._session_dir)):
            return None
        else:
            os.mkdir(self._session_dir)
        
        return session_name
    
    def createLog(self, session_name):
        """
        Creates directory to save log data to, returns name of log. Used when
        stand is acquiring data while not producing a plasma.
        
        Parameters:
            session_name (str): name of the logging session

        Returns:
            session_name (str): name of the logging session, empty string if creating directory failed
        """
        session_dir = os.path.dirname(os.path.realpath(__file__)) + "\\DATA_LOGS\\" + session_name + "\\"
        if os.path.exists(session_dir):
            return ""
        
        self._session_dir = session_dir
             

        os.mkdir(self._session_dir)
        
        session_name = self.generateShotName(session_name)
                
        return session_name        

    def addDevice(self, device_name, acquisition_type, data_names):
        """
        Creates a log file in the data logging session's directory for the given
        input device.
        
        Parameters:
            device_name (str): name of the device
            acquisition_type (str): type of data acquisition for the device,
                typically "INPUT" or "OUTPUT" denoting if the device is recording
                data from sensors or sending commands to the stand, respectively.
                could be used for other applications.
            data_names (list(str)): names of data sterams the device will be saving.
                these will be the column names in the csv file.

        Returns:
            None
        """
        if not os.path.exists(self._session_dir + "RAW_DATA\\"):
            os.mkdir(self._session_dir + "RAW_DATA\\")
        path = self._session_dir + "RAW_DATA\\" + device_name + "_" + acquisition_type + ".csv"
            
        with open(path, mode="w", newline="") as file:
            writer = csv.writer(file, delimiter = ",")
            writer.writerow(data_names)
        
    def saveData(self, device_name, acquisition_type, data):
        """
        Saves data from a device into the database.
        
        Parameters:
            device_name (str): name of the device
            acquisition_type (str): type of data acquisition for the device,
                typically "INPUT" or "OUTPUT" denoting if the device is recording
                data from sensors or sending commands to the stand, respectively.
                could be used for other applications.
            data (nd.array): 2D array of the data to be saved. columns are each
                of the named data streams, rows are each point data was taken
                (typically associated with a time value).

        Returns:
            None
        """
        if len(data) == 0:
            return
        path = self._session_dir + "RAW_DATA\\" + device_name + "_" + acquisition_type + ".csv"
        
        with open(path, mode="a", newline="") as file:
            writer = csv.writer(file, delimiter = ",")
            for i in range(0, len(data[:,0])):
                writer.writerow(data[i,:])
    
    def saveSettings(self, setting_data):
        """Saves logging settings dict to the database."""
        path = self._session_dir + "settings.json"
        if os.path.exists(path):
            data_dict = json.load(open(path, mode="r"))
        else:
            data_dict = {}    
        
        data_dict.update(setting_data)
        

        json.dump(data_dict, open(path, mode="w"))        
        
        #self.writeXL(setting_data)
            
        
class AnalysisDataManager:
    """
    A class to used by analysis code to manage database interactions.

    ...

    Attributes
    ----------
    _session_dir : str
        the directory data is read from and saved to
    _cached_analysis : dict
        most recent analysis loaded from database, since data is typically
        requested from files in groups, this improves speed of program
    _cached_analysis_name : str
        name of analysis that is currently cached
    _session_type : str
        specifies whether session being analyzed was a "LOG" data logging session
        (no plasma) or a "SHOT" data ogging session

    Methods
    -------
    _getData(str, list(str), bool) : dict/DataFrame
    __convertStrStyle(str) : str
    _processRawData() : dict
    mapRaw(list(str), func(nd.array(float): float)) : None
    saveAnalysis(str, dict) : None
    getAnalysis(str, list(str)) : dict
    hasAnalysis(str, list(str)) : bool
    _processSettings() : dict
    """
    
    def __init__(self, session_type = None, session_name = None, reload_raw = False):     
        """
        Parameters:
            session_type (str): specifies whether session being analyzed was a
                "LOG" data logging session (no plasma) or a "SHOT" data logging session
            session_name (str): name of the data logging session
            reload_raw (bool): program will process raw data only on first time analysis
                code is called on a given data logging session. setting this to true
                overrides this and reloads the data regardless on if it has been
                processed before.
        """
        if session_type == "SHOT" and session_name is not None:
            self._session_dir =  os.path.dirname(os.path.realpath(__file__)) + "\\SHOT_DATA\\" + session_name + "\\"
        elif session_type == "LOG" and session_name is not None:
            self._session_dir = os.path.dirname(os.path.realpath(__file__)) + "\\DATA_LOGS\\" + session_name + "\\"
        elif session_type == "MULTI" and session_name is not None:
            self._session_dir = os.path.dirname(os.path.realpath(__file__)) + "\\MULTI_ANALYSIS\\" + session_name + ".p"
        else:
            self._session_dir = None
            
        self._cached_analysis_name = None
        self._cached_analysis = None
        self._session_type = session_type
        
        if reload_raw:
            self._processRawData()
    
    def _getData(self, file_name, columns = None, data_frame = False):
        """
        Gets raw data from a device in the database.
        
        Parameters:
            file_name (str): name of the file to pull data from, takes the format
                DEVICENAME_ACQUISITIONTYPE from saveData in DataManagerControl
            columns (str): name of the data streams to get, if None, gets all
                data from the file
            data_frame (nd.array): if True, returns a dataframe of the data,
                otherwise, returns dict

        Returns:
            dict/DataFrame
            
        TODO:
            This method is kinda old and no longer used in the same way. columns and
            data_frame parameters no longer needed -- just return all columns and
            always in data frame format
        """
        path = self._session_dir + "RAW_DATA\\"  + file_name
            
        if isinstance(columns, str):
            df = pd.read_csv(path, usecols=[columns])
        else:
            df = pd.read_csv(path, usecols=columns)
        
        if data_frame:
            return df
        
        if isinstance(columns, str):
            return np.array(df[columns])
        else:
            return df.to_dict(orient="list")
    
    def __convertStrStyle(self, string):
        """Converts a string from control code format into analysis code string format and returns it."""
        string = string.lower()
        string = string.replace("_", " ")
        return string
        
    def _processRawData(self):
        """
        Processes raw data saved from control code into a nice pickled dictionary
        for the analysis code to easily access. If control code is modified or
        new devices are added that require special handling, modify this method
        or make a subclass that reimplements this method (the latter is
        recommended). Default handling is to create a dictionary with keys of
        the column names and values an nd.array with the column's values.

        Returns:
            dict
        """
        # gettings a reference time for the session, either the time the shot
        # starts or the time logging starts.
        if self._session_type == "SHOT":
            ref_time = self.getAnalysis("settings", "shot start time")
        elif self._session_type == "LOG":
            ref_time = self.getAnalysis("settings", "log start time")
        
        # opening data
        dirs = os.listdir(os.path.dirname(self._session_dir + "RAW_DATA\\"))
        data_dict = {}
        for data_file in dirs:
            data_name = data_file[:-4] # remove .csv from string
            temp_data = self._getData(data_file, data_frame = True) # load data
            
            ### SPECIAL HANDLING HERE ###
            
            # spectroscopy data saved with wavelengths and time as column names
            # resaves time and wavelength as their own data values for easy access
            if data_name == "SPECTROMETER_INPUT":
                data_dict[self.__convertStrStyle(data_name + "_" + "TIME")] = np.array(temp_data.pop("TIME")) - ref_time
                data_dict[self.__convertStrStyle(data_name + "_" + "WAVELENGTH")] = np.array([float(col) for col in temp_data.columns])
                data_dict[self.__convertStrStyle(data_name + "_" + "COUNTS")] = [np.array(temp_data.iloc[i,:]) for i in range(0, len(temp_data.iloc[:,0]))]
                data_dict[self.__convertStrStyle(data_name + "_" + "BACKGROUND")] = [np.array(temp_data.iloc[i,:]) for i in range(0, len(temp_data.iloc[:,0]))][0]
           
            ### DEFAULT HANDLING ###
            # used if data_name not specified in special handling section
            else:
                for column in temp_data.columns:
                    if column[-4:] == "TIME": # TODO: not in love with handling
                        data_dict[self.__convertStrStyle(data_name + "_" + column)] = np.array(temp_data[column]) - ref_time
                    else:
                        data_dict[self.__convertStrStyle(data_name + "_" + column)] = np.array(temp_data[column])
        
        print([key for key in data_dict.keys()])
        return data_dict

    def mapRaw(self, params, func):
        """
        If raw data was somehow messed up during logging, (for example, calibration
        of sensor values or shifting of time values to a reference time is done
        incorrectly), this provides a way to alter raw values. It does NOT alter
        the raw data files, instead alters processed raw data file saved in
        analysis.
        
        Parameters:
            params (str/list(str)): single parameter or list of parameters  or to be mapped
            func (func(nd.array(float)): float): function to map values with
            
        Returns:
            None
        """
        self.getAnalysis("raw")
        if isinstance(params, str):
            params = [params]
        for param in params:
            self._cached_analysis[param] = func(self._cached_analysis[param])
        p.dump(self._cached_analysis, open(self._session_dir + "ANALYSIS\\raw.p", mode="wb"))
        
    def saveAnalysis(self, analysis_name, new_data):
        """
        Saves analysis to database.
        
        Parameters:
            analysis_name (str): name of analysis module. Corresponds to file
                name analysis will be saved under.
            new_data (dict): the data to be saved to the file.
        """
        if analysis_name == "raw": #Don't overwrite this file, use mapRaw instead
            raise ValueError("Don't use saveAnalysis to edit raw data. Use mapRaw instead")
            return
        
        path = self._session_dir + "ANALYSIS\\" + analysis_name + ".p"
        self.getAnalysis(analysis_name)    
        
        self._cached_analysis.update(new_data)
        p.dump(self._cached_analysis, open(path, mode="wb"))
        
    def getAnalysis(self, analysis_name, columns = None):
        """
        Gets raw data or previous analysis results for analysis
        
        Parameters:
            analysis_name (str): name of analysis module data is from. could
                be from analysis classes, "raw", or "settings"
            columns (list(str)): data columns from the analysis module to get. None
            returns all data in the module.
            
        Returns:
            dict
        """
        if not os.path.exists(self._session_dir + "ANALYSIS\\"):
                os.mkdir(self._session_dir + "ANALYSIS\\")
                
        if analysis_name == "raw" and not os.path.exists(self._session_dir + "ANALYSIS\\raw.p"):
            self._cached_analysis = self._processRawData()
            p.dump(self._cached_analysis, open(self._session_dir + "ANALYSIS\\raw.p", mode="wb"))
            self._cached_analysis_name = "raw"
        if analysis_name == "settings" and not os.path.exists(self._session_dir + "ANALYSIS\\settings.p"):
            self._cached_analysis = self._processSettings()
            p.dump(self._cached_analysis, open(self._session_dir + "ANALYSIS\\settings.p", mode="wb"))
            self._cached_analysis_name = "settings"   
        
        if analysis_name != self._cached_analysis_name:
            path = self._session_dir + "ANALYSIS\\" + analysis_name + ".p"
            
            if os.path.exists(path):
                self._cached_analysis = p.load(open(path, mode="rb"))
            else:
                self._cached_analysis  = {}
            self._cached_analysis_name = analysis_name
        
        if columns is None:
            return self._cached_analysis
        elif isinstance(columns, str):
            return self._cached_analysis[columns]
        else:
            return {key: self._cached_analysis[key] for key in columns}
        
    def hasAnalysis(self, analysis_name, columns):
        """Returns whether a given analysis module has the specified saved data columns"""
        if isinstance(columns, str):
            columns = [columns]
        
        if analysis_name != self._cached_analysis_name:
            path = self._session_dir + "ANALYSIS\\" + analysis_name + ".p"
            if not os.path.exists(path):
                return False
            self._cached_analysis = p.load(open(path, mode="rb"))
            self._cached_analysis_name = analysis_name
            
        return all([column in self._cached_analysis for column in columns])
    
    def _processSettings(self):
        """Processes and returns the raw settings saved by control code."""
        path = self._session_dir + "settings.json"
        data = json.load(open(path, mode="r"))
        processed_data = {}
        for col in data:
            processed_data[self.__convertStrStyle(col)] = data[col]
        print([key for key in processed_data.keys()])
        return processed_data