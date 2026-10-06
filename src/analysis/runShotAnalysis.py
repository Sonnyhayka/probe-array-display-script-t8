# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 09:22:05 2025

@author: NeutralBeams2
"""

import matplotlib.pyplot as plt
import numpy as np
from paths import SHOT_DATA_DIR
from .langmuir_support_functions import (
    OMLfit,
    analyzeTotal,
    apply_butter_filter,
    apply_notch_filters,
    calcParameters,
    calcProbeArea,
    fitDoubletemp,
    fitExponential,
    get_resets_1,
    get_sweepN,
    obtainFromTe,
    plot_sweep,
    smooth,
)
#from random import *
from scipy.signal import savgol_filter
import pandas as pd
from scipy.ndimage import gaussian_filter1d


def runShotAnalysis(shotnumber, start_time=0.2, end_time=0.2, power_sweep = False, display_amount=0, show_plots = False, ask_user = False):
    
    ############ Determine which shot and which gas is used ###################
    base_dir = SHOT_DATA_DIR / str(shotnumber)
    df = pd.read_csv(base_dir / "RAW_DATA" / "LAB_JACK_INPUT.csv")
    #df_RF = pd.read_csv(fr'{base_dir}\RAW_DATA\RF_SOURCE_OUTPUT.csv')
    GAS=39.948  # Atomic mass of gas
    
    # ############ Determine the start of plasma by the photodiode signal ##################
    # photodiode = df["PHOTODIODE"].values - df["PHOTODIODE"].values[0]
    time = df["TIME"].values - df["TIME"].values[0]
    time = np.linspace(time[0], time[-1], num=len(time))
    #plasma_start_index = np.argmax(photodiode > 0.1)
    # plasma_end_index = len(photodiode) - np.argmax(photodiode[::-1] > 0.1) - 1
    
    ############ Determine the sample frequency ###################
    if ask_user:
        user_input = input("Sample frequency (Hz)? Press enter if you don't know: ").strip()
        if user_input == "":
            datarate = len(time)/time[-1]
            print(f"Sample frequency: {datarate}")
        else:
            datarate = int(user_input)
    else:
        datarate = len(time)/time[-1]
        print(f"Sample frequency: {datarate}")
    
    # ############ Ask between which times user wants to analyze the data #################
    # print(f"Plasma was on from t={time[plasma_start_index]} and t={time[plasma_end_index]} seconds")
    # if ask_user:
    #     ti = input(f"Start time? Press enter to start from t={time[plasma_start_index]+start_time} s ").strip()
    #     tf = input(f"Stop time? Press enter to start from t={time[plasma_end_index]-end_time} s ").strip()
    #     if ti == "":
    #         ti = time[plasma_start_index]+start_time
    #     else:
    #         ti = float(ti)
    #     if tf == "":
    #         tf = time[plasma_end_index]-end_time
    #     else:
    #         tf = float(tf)
    # else:
    #     ti = time[plasma_start_index]+start_time
    #     tf = time[plasma_end_index]-end_time
    
    # start_index = np.argmax(time>=ti)
    # end_index = np.argmax(time>=tf)
    
    start_index = 0
    end_index = len(time)
    
    ############ Load only data given by user to analyze ###################
    time = time[start_index:end_index]
    voltage = df["LANG_VOL"].values[start_index:end_index]
    current_1 = df["LANG_CUR_1"].values[start_index:end_index]
    current_2 = df["LANG_CUR_2"].values[start_index:end_index]
    current_3 = df["LANG_CUR_3"].values[start_index:end_index]
    current_4 = df["LANG_CUR_4"].values[start_index:end_index]
    current_5 = df["LANG_CUR_5"].values[start_index:end_index]
    
    current = [current_1, current_2, current_3, current_4, current_5]
    if power_sweep:
        synchron_time = df["TIME"].values[start_index:end_index]
    
    ############ Determine where the resets occur and if the sweep is rising/falling #################
    resets, falling = get_resets_1(voltage)
    num_sweeps = len(resets)-1
    print(f"Number of sweeps: {num_sweeps}")
    
    ############ Determine the sweeping frequency ###################
    if ask_user:
        user_input = input("Sweeping frequency (Hz)? Press enter if you don't know: ").strip()
        if user_input == "":
            if np.any(falling) and ~np.all(falling):
                sweep_freq = num_sweeps/(time[resets[-1]-1]-time[resets[0]])/2
            else:
                sweep_freq = num_sweeps/(time[resets[-1]-1]-time[resets[0]])
            print(f"Sweep frequency: {sweep_freq}")
        else:
            sweep_freq = float(user_input)
    else:
        if np.any(falling) and ~np.all(falling):
            sweep_freq = num_sweeps/(time[resets[-1]-1]-time[resets[0]])/2
        else:
            sweep_freq = num_sweeps/(time[resets[-1]-1]-time[resets[0]])
        print(f"Sweep frequency: {sweep_freq}")
    
    ############ Apply an array of notch filters to the current measurement ####################
    num_harmonics = 4       # Number of harmonics of 360 Hz to filter out: 360, 720, etc
    num_freq = 10           # Number of sample frequencies away from every harmonic to filter out: 360 +- sweep_freq, 360 +- 2*sweep_freq, etc.
    fs = datarate           # Sample frequency
    Q = 200                 # The bandwidth (Q-factor) of notch filter, high Q means narrow band     
    filtered_current_1 = apply_notch_filters(current_1, num_harmonics, num_freq, Q, fs, sweep_freq)   
    filtered_current_2 = apply_notch_filters(current_2, num_harmonics, num_freq, Q, fs, sweep_freq)   
    filtered_current_3 = apply_notch_filters(current_3, num_harmonics, num_freq, Q, fs, sweep_freq)   
    filtered_current_4 = apply_notch_filters(current_4, num_harmonics, num_freq, Q, fs, sweep_freq)   
    filtered_current_5 = apply_notch_filters(current_5, num_harmonics, num_freq, Q, fs, sweep_freq)   

    filtered_current = [filtered_current_1, filtered_current_2, filtered_current_3, filtered_current_4, filtered_current_5]
    ############ Ask user if they want reference probe voltage to be subtracted ###################
    if ask_user:
        user_input = input("Subtract reference probe voltage [y/n]? ").strip()
        while user_input != "y" and user_input != "n":
            user_input = input("Please type y or n: ").strip()
        if user_input == "y":
            ref_voltage = df["LANG_REF_VOL"].values[start_index:end_index]
            voltage = voltage-ref_voltage
        
    ############ Ask user if user wants to completely analyze or only partially ###################
    if ask_user:
        user_input = input("Completely analyze [y/n]? ").strip()
        while user_input != "y" and user_input != "n":
            user_input = input("Please type y or n: ").strip()
        complete_analyze = user_input == "y"
    else:
        complete_analyze = False
    
    ########### Ignore sweeps on beginning and end of sweep based on what kind of sweep it is ################
    symmetric_sweep = False
    if np.all(falling):
        skip_first_points = 5
        skip_last_points = 3
    elif np.any(falling):
        skip_first_points = 1
        skip_last_points = 1
        symmetric_sweep = True
    else:
        skip_first_points = 5
        skip_last_points = 3
    
    N_combine = 10
    
    if symmetric_sweep:
        data_length = num_sweeps - 2*N_combine + 2
    else:
        data_length = num_sweeps - N_combine + 1
    
    ########### Create stored data arrays #####################
    ion_densities = []
    ion_densitie_errors = []
    electron_densities = []
    electron_densitie_errors = []
    electron_temperatures = []
    electron_temperature_errors = []
    plasma_potentials = []
    floating_potentials = []
    sweep_times = []
    
    for i in np.arange(0, 5):
        ion_densities.append(np.zeros(data_length))
        ion_densitie_errors.append(np.zeros(data_length))
        electron_densities.append(np.zeros(data_length))
        electron_densitie_errors.append(np.zeros(data_length))
        electron_temperatures.append(np.zeros(data_length))
        electron_temperature_errors.append(np.zeros(data_length))
        plasma_potentials.append(np.zeros(data_length))
        floating_potentials.append(np.zeros(data_length))
        sweep_times.append(np.zeros(data_length))
        
    if power_sweep:
        powers_all = np.zeros(data_length, dtype=int) 
        powers = []
    
    ########## Set how many times the data should be plotted and printed out #################  
    if display_amount != 0:
        display_indices = np.arange(0.5, display_amount)*num_sweeps/display_amount
        display_indices = display_indices.astype(int)
    else:
        display_indices = []
    
    
    ########### Set initial values of parameters ##################
    p0 = [0.67, 0.076, 17.4, -5.4]
    p0_exp = [3, 1e17]
    
    for j in range(0, 5):
        for i in range(0, data_length):
            sweep_voltage, sweep_current, sweep_filtered_current = get_sweepN(voltage, current[j], filtered_current[j], resets, N_combine, i, num_sweeps, skip_first_points, skip_last_points, symmetric_sweep)
            sweep_time = time[resets[i]]
            sweep_times[j][i] = sweep_time
            
            if i in display_indices:
                display = True
                _print = True
            else:
                display = False
                _print = False
                
            sweep_length = len(sweep_voltage)
            window_length = int(0.05*(sweep_length))
            if window_length % 2 == 0:
                window_length += 1
            sweep_filtered_current = savgol_filter(sweep_filtered_current, window_length=window_length, polyorder=3)
            sweep_filtered_current = savgol_filter(sweep_filtered_current, window_length=window_length, polyorder=2)
            sweep_filtered_current = savgol_filter(sweep_filtered_current, window_length=window_length, polyorder=1)
            sweep_filtered_current = savgol_filter(sweep_filtered_current, window_length=window_length, polyorder=1)
            sweep_filtered_current = savgol_filter(sweep_filtered_current, window_length=window_length, polyorder=1)
            
            # sigma = int(0.01*sweep_length)
            # sweep_filtered_current = gaussian_filter1d(sweep_filtered_current, sigma)
            # sweep_filtered_current = gaussian_filter1d(sweep_filtered_current, sigma)
            # sweep_filtered_current = gaussian_filter1d(sweep_filtered_current, sigma)
            # sweep_filtered_current = gaussian_filter1d(sweep_filtered_current, sigma)
                    
            if complete_analyze:
                n_e, n_i, lambda_D, T_e, T_eH, hot_fraction, p0, n_i_oml, err_n_i_oml, T_e_2, n_e_2, err_T_e, err_n_e, p0_exp, plasma_potential, floating_potential = analyzeTotal(sweep_time, sweep_voltage, sweep_current, sweep_filtered_current, datarate, GAS=GAS, previous_p0 = p0, previous_p0_exp = p0_exp, window_length=window_length, display=display, _print=_print)
                
                ion_densities[j][i] = n_i_oml  
                ion_densitie_errors[j][i] = err_n_i_oml
                electron_densities[j][i] = n_e_2
                electron_densitie_errors[j][i] = err_n_e
                electron_temperatures[j][i] = T_e_2
                electron_densitie_errors[j][i] = err_T_e
                plasma_potentials[j][i] = plasma_potential
                floating_potentials[j][i] = floating_potential
                
            else:
                arg_floating_potential, floating_potential, arg_plasma_potential, plasma_potential, I_e, I_i = calcParameters(sweep_time, sweep_voltage, sweep_current, sweep_filtered_current, datarate, window_length, display, _print)
                probe_area = calcProbeArea()
                
                n_i, err_n_i, slope_oml, intercept_oml = OMLfit(sweep_time, sweep_voltage, sweep_current, floating_potential, probe_area, GAS, display, _print)
                   
                T_e_2, n_e_2, err_T_e, err_n_e, p0_exp = fitExponential(sweep_time, sweep_voltage, sweep_current, arg_floating_potential, arg_plasma_potential, floating_potential, plasma_potential, probe_area, p0_exp, slope_oml, intercept_oml, display, _print)
                
                ion_densities[j][i] = n_i
                ion_densitie_errors[j][i] = err_n_i
                electron_densities[j][i] = n_e_2
                electron_densitie_errors[j][i] = err_n_e
                electron_temperatures[j][i] = T_e_2
                electron_densitie_errors[j][i] = err_T_e
                plasma_potentials[j][i] = plasma_potential
                floating_potentials[j][i] = floating_potential
            
        # if power_sweep:
        #     start_synchron_time = synchron_time[resets[i]]
        #     power = df_RF.loc[df_RF['TIME'] <= start_synchron_time , 'TARGET POWER'].tolist()[-1]
        #     powers_all[i] = power
        #     if i == 0 or powers_all[i] != powers[-1]:
        #         powers.append(power)
    
    if power_sweep:
        ion_density_averaging = {
            'Power' : powers_all,
            'Density': ion_densities
        }
        
        ion_density_averaging_df = pd.DataFrame(ion_density_averaging)
        
        ion_density_averages = np.zeros(len(powers))
        density_errors = np.zeros(len(powers))
        
        for i in range(len(powers)):
            values = ion_density_averaging_df.loc[ion_density_averaging_df['Power'] == powers[i], 'Density']
            ion_density_averages[i] = values.mean().item()
            density_errors[i] = values.std()
        
    if show_plots:
        for i in range(0, 5):
            plot_sweep(time, voltage, current[i], "Voltage (V)", "Current (mA)", i + 1, filtered_signal=filtered_current[i]) 
            
            plt.figure(f"Shot: {shotnumber} Density vs time, probe " + str(i + 1))
            plt.title("Density vs time")
            plt.xlabel("Time (s)")
            plt.ylabel("Density (m^-3)")
            plt.scatter(sweep_times[i], ion_densities[i], label="Ion density")
            plt.scatter(sweep_times[i], electron_densities[i], label="Electron density")
            plt.legend()
            plt.grid(True)
            plt.show()
        
            if power_sweep:
                plt.figure(f"Shot: {shotnumber} Ion density vs power (averaged)")
                plt.title("Ion density vs power")
                plt.xlabel("Power (W)")
                plt.ylabel("Ion density (m^-3)")
                plt.scatter(powers_all, ion_densities)
                plt.grid(True)
                plt.show()
                
                plt.figure(f"Shot: {shotnumber} Ion density vs power")
                plt.title("Ion density vs power")
                plt.xlabel("Power (W)")
                plt.ylabel("Ion density (m^-3)")
                plt.scatter(powers, ion_density_averages)
                plt.errorbar(powers, ion_density_averages, yerr = density_errors, fmt = 'o', ecolor = 'red', capsize = 3)
                plt.grid(True)
                plt.show()
    
            plt.figure(f"Shot: {shotnumber} Potentials vs time, probe " + str(i + 1))
            plt.title("Potentials vs time")
            plt.xlabel("Time (s)")
            plt.ylabel("Potential (V)")
            plt.scatter(sweep_times[i], floating_potentials[i], label="Floating potential")
            plt.scatter(sweep_times[i], plasma_potentials[i], label="Plasma potential")
            plt.legend()
            plt.grid(True)
            plt.show()
            
            plt.figure(f"Shot: {shotnumber} Electron temperature vs time, probe " + str(i + 1))
            plt.title("Electron temperature vs time")
            plt.xlabel("Time (s)")
            plt.ylabel("Electron temperature (eV)")
            plt.scatter(sweep_times[i], electron_temperatures[i], label="Electron temperature")
            plt.legend()
            plt.grid(True)
            plt.show()
    
    if power_sweep:
        return powers, ion_density_averages, density_errors
    else:
        return ion_densities, ion_densitie_errors, electron_densities, electron_densitie_errors, electron_temperatures, electron_temperature_errors, plasma_potentials, floating_potentials