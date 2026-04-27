# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:14:28 2023

@author: Noah Haggerty
"""

import numpy as np
import re
from scipy.signal import butter, sosfiltfilt
from scipy.optimize import curve_fit

#How to use:
#import sys
#sys.path.insert(0, '..\\UTILS')

def find(val, array, return_index = True, sorted_array = True, selection_method = "lower", extrapolate = True, print_me = False):
    # Binary search-ish
    array = np.array(array)
    if sorted_array:
        index = int(np.floor(len(array) / 2))
        search_size = index
        found = False
        
        if val <= array[0]:
            index = 0
            found = True
            if print_me:
                print("LOWER BOUNDS")
            if not extrapolate:
                index = None
                found_val = None
        elif val >= array[-1]:
            index = len(array) - 1
            found = True
            if print_me:
                print("UPPER BOUNDS")
            if not extrapolate:
                index = None
                found_val = None
                
        while not found:
            search_size = np.ceil(search_size / 2)
            if array[index] <= val and array[index + 1] >= val:
                if print_me:
                    print("FOUND: " + str(array[index]) + ", " + str(val) + ", " +str(array[index + 1]))
                found = True
                found_val = array[index]
                if selection_method == "lower" or (selection_method == "closest" and abs(array[index + 1] - val) < abs(array[index] - val)):
                    index += 1
            elif array[index] > val:
                index = max(int(round(index - search_size)), 0)
            elif array[index + 1] < val:
                index = min(int(round(index + search_size)), len(array) - 1)
    else:
        index = 0
        found_val = array[0]
        diff = abs(array[0] - val)
        for i in range(0, len(array)):
            if abs(array[i] - val) < diff:
                index = i
                found_val = array[i]
                diff = abs(array[i] - val)
        
    if return_index:
        return index
    else:
        return found_val
 

def mapArray(vals, val_array, map_array, selection_method = "lower"):
    map_vals = []
    for map_val in map_array:
           index = find(map_val, val_array, selection_method)
           map_vals.append(vals[index])
    return map_vals

def extractNums(string):
    number = r"[\d.]+"
    results = re.findall(number, string)
    results = [float(result) for result in results]
    return results

def frequencyNoiseFilter(signal, sample_rate, cutoff = 30):
    sos = butter(5, cutoff / (0.5 * sample_rate), btype='low', analog=False, output="sos")
    return sosfiltfilt(sos, signal, padlen= 500) # TODO: better padlen choice -- will this break in some cases bc it's a high fixed number?
    #return lfilter(b, a, signal)


def loadLxcat(file):
    file = open(file, 'r')
    lines = file.readlines()
    energies = []
    cross_sections = []
    num = r"\d+\.\d+e[\+\-]\d+"
    for line in lines:
        if len(re.findall(num, line)) == 2: #TODO: not the best handling
            nums = re.findall(num, line)
            energies.append(float(nums[0]))
            cross_sections.append(float(nums[1]))
            
    return {"energy": energies, "cross section": cross_sections}


def quickCalibrationFunc(x_data, y_data):
    def fitFunc(x, m, b): 
        return (m*x) + b
    
    fit_vals, covariance = curve_fit(fitFunc, np.array(x_data), np.array(y_data))
    
    def calFunc(x):
        return fitFunc(x, *fit_vals)
        
    return calFunc