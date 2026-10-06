import matplotlib.pyplot as plt
import scipy
from scipy.signal import savgol_filter, find_peaks_cwt
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import griddata
from scipy.signal import butter, filtfilt, iirnotch, sosfilt, sosfiltfilt, tf2sos
from scipy.ndimage import gaussian_filter1d
from scipy.stats import linregress
from . import callibration
import warnings



def get_figure_by_title(title):
    # Loop through all open figures
    for num in plt.get_fignums():
        fig = plt.figure(num)
        mgr = plt.get_current_fig_manager()
        
        # Try getting the window title (backend-specific)
        try:
            if mgr.window.windowTitle() == title:  # Qt5Agg backend
                return fig
        except AttributeError:
            try:
                if mgr.window.wm_title() == title:  # TkAgg backend
                    return fig
            except Exception:
                pass
    return None

def get_sweepN(voltage, current, filtered_current, resets, N_combine, i, num_sweeps, skip_first_points, skip_last_points, symmetric_sweep):
    if symmetric_sweep:
        N = min(N_combine, 1+(num_sweeps-i-1)//2)
        data_length = 0
        for j in range(0,2*N,2):
            data_length += resets[i+j+1]-resets[i+j]-(skip_first_points+skip_last_points)
    else:
        N = min(N_combine, num_sweeps-i)
        data_length = resets[i+N]-resets[i]-(N-1)*(skip_first_points+skip_last_points)  
    sweep_voltage = np.zeros(data_length)
    sweep_current = np.zeros(data_length)
    sweep_filtered_current = np.zeros(data_length)
    
    if symmetric_sweep:
        sweep_range = np.arange(0,2*N,2)
    else:
        sweep_range = np.arange(N)
      
    first_idx = 0
    for j in sweep_range:
        start = resets[i+j]+skip_first_points
        end = resets[i+j+1]-skip_last_points
        sweep_voltage[first_idx:(end-start+first_idx)] = voltage[start:end]
        sweep_current[first_idx:(end-start+first_idx)]  = current[start:end]
        sweep_filtered_current[first_idx:(end-start+first_idx)]  = filtered_current[start:end]
        first_idx += end-start
            
    sorted_arguments = np.argsort(sweep_voltage)
    sweep_voltage = sweep_voltage[sorted_arguments]
    sweep_current = sweep_current[sorted_arguments]
    sweep_filtered_current = sweep_filtered_current[sorted_arguments]
    
    return sweep_voltage, sweep_current, sweep_filtered_current

def get_resets_1(potential):
    resets = np.array([], dtype="int")
    falling = np.array([], dtype="bool")
    last_k = 0
    i = 0
    for k in range(1,len(potential)-1):
        if(abs(potential[k]-potential[k-1]) > 5) or np.sign(potential[k]-potential[k-1]) != np.sign(potential[k+1]-potential[k]):
            if k > last_k+20:
                resets = np.append(resets, k)
                if i != 0:
                    if potential[resets[i]-5]-potential[resets[i-1]+5] < 0:
                        falling = np.append(falling, True)
                    else:
                        falling  = np.append(falling, False)
                last_k = k
                i += 1
    return resets, falling

def get_resets_2(potential):
    falling_resets = np.array([], dtype="int")
    rising_resets = np.array([], dtype="int")
    last_k = 0
    for k in range(1,len(potential)-1):
        if(abs(potential[k]-potential[k-1]) > 5) or np.sign(potential[k]-potential[k-1]) != np.sign(potential[k+1]-potential[k]):
            if k > last_k+20:
                if np.sign(potential[k]-potential[k-1]) < 0:
                    falling_resets = np.append(falling_resets, k)
                else:
                    rising_resets = np.append(rising_resets, k)
                last_k = k
    return falling_resets, rising_resets

def plot_sweep(time, potential, signal, labela, labelb, probe_number, filtered_signal = []):
    plt.figure('Sweep Characteristics, probe ' + str(probe_number))    #Figure 5
    plt.plot(time, potential, 'k', label=labela)
    plt.ylabel(labela)
    plt.xlabel("Time(s)")
    plt.title("Voltage and current generated, probe " + str(probe_number), fontsize=16, fontweight='bold')
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2)
    
    ax2 = plt.twinx()                       
    ax2.scatter(time, 1000*signal, label=labelb)
    ax2.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=0) 
    if not len(filtered_signal) == 0:
        ax2.plot(time, 1000*filtered_signal, 'y', label="Filtered "+labelb)
    ax2.set_ylabel(labelb)
    ax2.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=1)
    
    plt.figure('Langmuir I-V, probe ' + str(probe_number))    #Figure 6
    plt.scatter(potential, 1000*signal)
    plt.ylabel(labelb)
    plt.xlabel(labela)
    plt.title("Langmuir's probe I-V Curves, probe " + str(probe_number),  fontsize=16, fontweight='bold')
   
    
    
    #for Langmuir probe manual calibration. 
    linreg = scipy.stats.linregress(potential, 1000*signal) #NOTE: ONLY for LP current read from power supply
    print()
    print("FOR MANUAL Langmuir probe CALIBRATION")
    print("Slope is:")
    print(linreg.slope)
    print("V/mA")
    print("Y-Intercept is:")
    print(linreg.intercept)
    print("mA")
    


###########################################################################
#Langmuir Potential vs Time data slicing to obtain individual I-V probe sweeps.
##############################################################################
#Slicing time index array created   (These values can be used to index the time array to show the times of individual traces) 


def stitch(potential, signala, signalb):    
    sort = np.argsort(potential)
    potential = potential[sort]
    signalb = signalb[sort]
    signala = signala[sort]
        
    cutoff = 35 #mA
    split_id = np.argmin(np.abs(signala-cutoff*0.001))
    conc = np.append(signala[0:split_id+1], signalb[split_id:-1])
    return [potential, conc]

def apply_notch_filters(data, num_harmonics, num_freq, Q, fs, sweep_freq):   
    combined_sos = np.zeros(shape=((2*num_freq+1)*num_harmonics + 6, 6))
    for h in range(1, num_harmonics+1):
        row = (h-1)*(2*num_freq+1)
        b, a = iirnotch(h*360, Q, fs)
        combined_sos[row,:] = tf2sos(b, a)
        for f in np.arange(1,num_freq+1):
            b, a = iirnotch(h*360 + f*sweep_freq, Q, fs)
            combined_sos[row+2*f-1] = tf2sos(b, a)
            b, a = iirnotch(h*360 - f*sweep_freq, Q, fs)
            combined_sos[row+2*f] = tf2sos(b, a)
            
    b, a = iirnotch(240, Q, fs)
    combined_sos[-6] = tf2sos(b, a)
    b, a = iirnotch(240 -sweep_freq, Q, fs)
    combined_sos[-5] = tf2sos(b, a)
    b, a = iirnotch(240 + sweep_freq, Q, fs)
    combined_sos[-4] = tf2sos(b, a)
    
    
    b, a = iirnotch(120, Q, fs)
    combined_sos[-3] = tf2sos(b, a)
    b, a = iirnotch(120 -sweep_freq, Q, fs)
    combined_sos[-2] = tf2sos(b, a)
    b, a = iirnotch(120 + sweep_freq, Q, fs)
    combined_sos[-1] = tf2sos(b, a)
  
    return sosfiltfilt(combined_sos, data)
    

def apply_butter_filter(data, num_harmonics, num_freq, fs, sweep_freq):
    #360*num_harmonics+num_freq*sweep_freq
    b, a = butter(6, 300, btype="low", analog=False, fs=fs)
    return sosfiltfilt(tf2sos(b,a), data)

def smooth(data, window_length, falling, polyorder=1):
    if falling:
        end_value = data[-1]
        pad = np.ones(window_length)*end_value
        padded_data = np.append(data, pad)
        smoothed_data = savgol_filter(padded_data, window_length=window_length, polyorder=polyorder, deriv=0)
        return smoothed_data[:-window_length]
    else:
        end_value = data[0]
        pad = np.ones(window_length)*end_value
        padded_data = np.append(pad, data)
        smoothed_data = savgol_filter(padded_data, window_length=window_length, polyorder=polyorder, deriv=0)
        return smoothed_data[window_length:]
    

def plasma_potentialFunc(v_f, T_e, gas='Ar'):
    # Physical constants
    m_e = 9.10938356e-31  # electron mass (kg)
    ion_masses = {
        'Ar': 6.63e-26,  # Argon ion mass (kg)
        'H': 1.67e-27,
        'D': 3.34e-27,
        'He': 6.65e-27,
        # Add others if needed
    }
    M_i = ion_masses.get(gas, 6.63e-26)  # default to Argon
    delta_V = T_e * np.log(np.sqrt(2 * np.pi * m_e / M_i))
    V_p = -1*(v_f + delta_V)
    return V_p

def func_double_lin(x, a, b, xk, yk):
    return np.piecewise(x, x < xk, [lambda x: yk - a * (xk - x), lambda x: yk + b * (x - xk)])

def calcParameters(time, voltage, current, filtered_current, datarate, window_length, display=False, _print=False):
    #Calibrate voltage
    path_resistance = callibration.probeR
    voltage = voltage-filtered_current*path_resistance
    
    ######################################
    #Calculate derivative with Gaussian filters
    ######################################
    # sigma = int(0.02*len(voltage))
    # filtered_derivative = np.gradient(filtered_current, voltage)
    # filtered_derivative = gaussian_filter1d(filtered_derivative, sigma)
    
    # filtered_second_derivative = np.gradient(filtered_derivative, voltage)
    # filtered_second_derivative = gaussian_filter1d(filtered_second_derivative, sigma)
   
    ######################################
    #Calculate derivative with savgol filters
    ######################################
   
    average_delta = np.mean(np.diff(voltage))
    filtered_derivative = savgol_filter(filtered_current, window_length, polyorder=1, deriv=1, delta = average_delta)
    #filtered_derivative = savgol_filter(filtered_derivative, window_length, polyorder=2, deriv=0)
    #filtered_derivative = savgol_filter(filtered_derivative, window_length, polyorder=1, deriv=0)
    #filtered_derivative = savgol_filter(filtered_derivative, window_length, polyorder=1, deriv=0)
    
    filtered_second_derivative = savgol_filter(filtered_derivative, window_length, polyorder=1, deriv=1, delta = average_delta)
    #filtered_second_derivative = savgol_filter(filtered_second_derivative, window_length, polyorder=2, deriv=0)
    #filtered_second_derivative = savgol_filter(filtered_second_derivative, window_length, polyorder=1, deriv=0)
    #filtered_second_derivative = savgol_filter(filtered_second_derivative, window_length, polyorder=1, deriv=0)
    
    if(display):
        fig, ax1 = plt.subplots()
        fig.canvas.manager.set_window_title("Langmuir trace at %.3f s" % time)
        
        raw_plot = ax1.scatter(voltage, 1e3*current, c='k', label = 'Raw data')
        filtered_plot = ax1.plot(voltage, 1e3*filtered_current, c='b', label = 'Filtered data')
        
        ax2 = ax1.twinx()
        derivative_plot = ax2.plot(voltage, 1e3*filtered_derivative, c='c', label = 'First derivative')
        
        ax3 = ax1.twinx()
        second_derivative_plot = ax3.plot(voltage, 1e3*filtered_second_derivative, c='r', label = 'Second derivative')

        ax1.set_xlabel("Bias (V)")
        ax1.set_ylabel("Current (mA)", )
        ax1.tick_params(axis='y', labelcolor="b")
        ax2.set_ylabel("dI/dV (mA/V)", c="c")
        ax2.tick_params(axis='y', labelcolor="c")
        ax3.set_ylabel("d2I/dV2 (mA/V2)", c="r")
        ax3.tick_params(axis='y', labelcolor="r")
        
        plots = [raw_plot]+filtered_plot+derivative_plot+second_derivative_plot
        labels = [p.get_label() for p in plots]
        
        ax1.grid(True)
        plt.title("Langmuir trace at %.3f s" % time)
        ax1.legend(plots, labels)
        plt.show()
    
    arg_floating_potential = np.argmin(np.abs(filtered_current))
    floating_potential = voltage[arg_floating_potential]
    
    arg_plasma_potential = np.argmax(np.logical_and(filtered_second_derivative <= 0, voltage>floating_potential))
    if arg_plasma_potential == 0:
        arg_plasma_potential = np.argmax(filtered_derivative)
    # arg_plasma_potential = -1
    plasma_potential = voltage[arg_plasma_potential]
    
    I_e = filtered_current[arg_plasma_potential]
    
    I_i = -np.mean(current[:20])
    
    if _print:
        print()
        print(f"############ Time = {time} ##############")
        print(f"Floating potential: {floating_potential}")
        print(f"Plasma potential: {plasma_potential}")
        print(f"Electron saturation current: {1e3*I_e}")
        print(f"Ion saturation current: {1e3*I_i}")
        
    return arg_floating_potential, floating_potential, arg_plasma_potential, plasma_potential, I_e, I_i

def fitDoubletemp(time, voltage, filtered_current, arg_floating_potential, floating_potential, arg_plasma_potential, 
                  plasma_potential, previous_p0, display=False, _print=False):
    
    voltage_exp = voltage[arg_floating_potential:arg_plasma_potential]
    current_exp = filtered_current[arg_floating_potential:arg_plasma_potential]
    mask = current_exp > 0
    voltage_exp = voltage_exp[mask]
    current_exp = current_exp[mask]
    current_log = np.log(current_exp)
    
    p0 = previous_p0
    bounds = ([0,0,0,-np.inf],[np.inf,np.inf,30,np.inf])
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")        
            popt, pcov = curve_fit(func_double_lin, voltage_exp, current_log, bounds=bounds, p0=p0)
            
            if not w:
                p0 = popt
        
        if(display):
            plt.figure("Exp sect at %.3f s" % time)
            plt.scatter(voltage_exp, current_log, c='k')
            plt.plot(voltage_exp, func_double_lin(voltage_exp, *popt), c='g')
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current logarithmic")
            plt.title("Exponential section at %.3f s" % time)
        
        T_eH = 1/popt[0]
        T_e = 1/popt[1]
        if(_print):
            print(" ")
            print("T_e estimate = %.3f eV" % T_e)
            print("T_eH estimate = %.3f eV" % T_eH)
    except:
        popt = previous_p0
        T_eH = np.nan
        T_e = np.nan
        print(f"TIME: {round(time,3)} s: Curve could not be fitted, proceeding with T_e = {T_e} V and T_eH = {T_eH} V from previous sweep.")
    
    
    #########################################
    ## Fit exponential section (refined)
    #########################################  
    
    arg_lower_ref = np.argmin(np.abs(voltage-(floating_potential+0.25*T_e)))
    arg_upper_ref = np.argmin(np.abs(voltage-(plasma_potential-0.2*T_e)))

    voltage_exp = voltage[arg_lower_ref:arg_upper_ref]
    current_exp = filtered_current[arg_lower_ref:arg_upper_ref]
    mask = current_exp > 0
    voltage_exp = voltage_exp[mask]
    current_exp = current_exp[mask]
    current_log = np.log(current_exp)  

    try:  
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  
            popt, pcov = curve_fit(func_double_lin, voltage_exp, current_log, bounds=bounds, p0=p0)
            if not w:
                p0 = popt
                T_eH = 1/popt[0]
                T_e = 1/popt[1]
                
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  
            hot_fraction = (popt[3] + popt[1] * (plasma_potential - popt[2])) - (popt[3] + popt[0] * (plasma_potential - popt[2]))
            hot_fraction = np.exp(-hot_fraction)
            if w:
                hot_fraction = np.nan
        
        if(display):
            plt.figure("Exp sect refined at %.3f s" % time)
            plt.scatter(voltage_exp, current_log, c='k')
            plt.plot(voltage_exp, func_double_lin(voltage_exp, *popt), c='g')
            plt.xlabel("Voltage (V)")
            plt.ylabel("Current logarithmic")
            plt.title("Exponential section (refined) at %.3f s" % time)
        
        if(_print):
            print(" ")
            print("T_e estimate = %.3f eV" % T_e)
            print("T_eH estimate = %.3f eV" % T_eH)
            #print("Hot fraction = %.3f" % hot_fraction)
    except:
        hot_fraction = np.nan
        print(f"TIME: {round(time,3)} s: Refined curve could not be fitted, proceeding with previous hot_fraction")
        
    return T_e, T_eH, hot_fraction, p0

def obtainFromTe(T_e, I_i, I_e, GAS, probe_area, _print=False):
    if np.isnan(T_e):
        return np.nan, np.nan, np.nan
    
    #Constants
    amu_const = 1.66e-27    #Electron mass
    e_const = 1.601e-19       #Electron charge
    #########################################
    ## Obtain n_e, n_i and lambda_D from T_e
    #########################################  
    
    if(_print):
        print("Probe area = %.3f mm2" % (probe_area*1e6))
         
    n_e = I_e/(probe_area*e_const*np.sqrt(T_e*e_const/(2*np.pi*9.1e-31)))
    if(_print):
         print("n_e estimate = %.3e m-3" % n_e)
     
    n_i = (I_i/(e_const*probe_area*np.sqrt(T_e*e_const/(GAS*amu_const))))
     
    if(_print):
         print("n_i estimate = %.3e m-3" % n_i)
     
    lambda_D = 743*np.sqrt(T_e/(n_e*1e-6))*1e-2 #m
    if(_print):
         print("Debye length estimate = %.3f um" % (lambda_D*1e6))
         print("GAS=",GAS)  
         
    return n_e, n_i, lambda_D

def OMLfit(time, voltage, current, floating_potential, probe_area, GAS, display=False, _print=False):
    #########################################
    ## OML theory
    #########################################  
    
    arg_I_i_tail = np.argmin(abs(voltage-floating_potential+20))
    voltage_low = voltage[0:arg_I_i_tail]
    current_low = current[0:arg_I_i_tail]
    current_low_squared = (1000*current_low)**2
    
    try:  
        slope, intercept, _, _, slope_err = linregress(voltage_low, current_low_squared)
        if(display):
            plt.figure("OML at %.3f s" % time) 
            plt.scatter(voltage_low, current_low_squared, label="Raw current")
            plt.plot(voltage_low, slope*voltage_low + intercept, c='g', label="OML fit")
            plt.xlabel("V")
            plt.ylabel("I$^2$ (mA2)")
            plt.legend()
            plt.title("OML theory at %.3f s" % time)
        n_i_oml = np.sqrt(-slope/(7.05**2*(probe_area*1e4)**2/GAS))*1e11*1e6 # Chen's formula for n_i11
        err_n_i_oml = np.sqrt(1/((7.05**2*(probe_area*1e4)**2/GAS)*-slope))*1e17/2*slope_err
        
        if(_print):
            print("n_i refined = %.3e m-3" % n_i_oml)
            print("Error in n_i_refined = %.3e m-3" % err_n_i_oml)
            
    except:
        n_i_oml = np.nan
        err_n_i_oml = np.nan
        slope = np.nan
        intercept = np.nan
        print(f"TIME: {round(time,3)} s: OML theory could not be fitted")
        
    return n_i_oml, err_n_i_oml, slope, intercept

def calcProbeArea():
    probe_l = callibration.probeL/1000#(1.90+2.05+2.04+2.01)/4000 #m
    probe_d = callibration.probeD/1000#(1.65+1.63+1.58+1.61)/4000 #3.19/1000
     
    return probe_l*np.pi*probe_d + np.pi*0.25*probe_d**2 #m2

def fitExponential(time, voltage, filtered_current, arg_floating_potential, arg_plasma_potential, floating_potential, plasma_potential, probe_area, previous_p0_exp, slope_oml, intercept_oml, display=False, _print=False):
    #Constants
    amu_const = 1.66e-27    #Electron mass
    e_const = 1.601e-19       #Electron charge
    
    
    #########################################
    ## Obtain ion and electron currents
    #########################################  
    def exp_func(x, _T_e, _n_e):
        return probe_area*_n_e*e_const*np.sqrt(_T_e*e_const/(2*np.pi*9.1e-31))*np.exp(-(plasma_potential-x)/_T_e)
    
    p0_exp = previous_p0_exp
    bounds = ([0,0],[np.inf,np.inf])
    #[T_e, n_e]
    
    voltage_exp = voltage[arg_floating_potential:arg_plasma_potential]
    current_exp = filtered_current[arg_floating_potential:arg_plasma_potential]
    
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  
            popt, pcov = curve_fit(exp_func, voltage_exp, current_exp, bounds=bounds, p0=p0_exp)
            if not w:
                p0_exp = popt
  
        T_e, n_e = popt
        err_T_e, err_n_e = np.sqrt(np.diag(pcov))
    
        if(_print):
            print()
            print(f"T_e = {T_e} eV and n_e = {n_e} m-3")
            print("Errors in T_e and n_e:")
            print(np.sqrt(np.diag(pcov)) / popt)
        
        I_e_fit = probe_area*n_e*e_const*np.sqrt(T_e*e_const/(2*np.pi*9.1e-31))*np.exp(-(plasma_potential-voltage)/T_e)
    
        plasma_potentialC = plasma_potentialFunc(floating_potential, T_e, gas='Ar')
        I_e_fitalt = probe_area*n_e*e_const*np.sqrt(T_e*e_const/(2*np.pi*9.1e-31))*np.exp(-(plasma_potentialC-voltage)/T_e)
        
        
        I_oml = np.zeros(len(voltage))
        if not np.isnan(slope_oml) and not np.isnan(intercept_oml):
            I_oml[:arg_floating_potential] = 1e-3*np.sqrt(slope_oml*voltage[:arg_floating_potential]+intercept_oml)
    
        I_fit = I_e_fit - I_oml
        I_fitalt = I_e_fitalt - I_oml
    
        I_fit[arg_plasma_potential:] = I_fit[arg_plasma_potential]
        I_fitalt[arg_plasma_potential:] = I_fitalt[arg_plasma_potential]
    
        
        
        if(display):
            fig = get_figure_by_title("Langmuir trace at %.3f s" % time)
            axes = fig.get_axes()
            axes[0].plot(voltage, 1000*I_fit, linewidth=3,label="Theory")      
            axes[0].plot(voltage, 1000*I_fitalt, linewidth=3,label="Theory")   
    except:
        T_e = np.nan
        n_e = np.nan
        err_T_e = np.nan
        err_n_e = np.nan
        
        
    return T_e, n_e, err_T_e, err_n_e, p0_exp

def analyzeTotal(time, voltage, current, filtered_current, datarate, GAS, previous_p0, previous_p0_exp, window_length, display=False, _print=False):
    
    probe_area = calcProbeArea()
    
    arg_floating_potential, floating_potential, arg_plasma_potential, plasma_potential, I_e, I_i = calcParameters(time, voltage, current, filtered_current, datarate, window_length, display, _print)

    T_e, T_eH, hot_fraction, p0 = fitDoubletemp(time, voltage, filtered_current, arg_floating_potential, floating_potential, arg_plasma_potential, plasma_potential, previous_p0, display, _print)
   
    n_e, n_i, lambda_D = obtainFromTe(T_e, I_i, I_e, GAS, probe_area, _print)
   
    n_i_oml, err_n_i_oml, slope_oml, intercept_oml = OMLfit(time, voltage, current, floating_potential, probe_area, GAS, display, _print)

    T_e_2, n_e_2, err_T_e, err_n_e, p0_exp = fitExponential(time, voltage, filtered_current, arg_floating_potential, arg_plasma_potential, floating_potential, plasma_potential, probe_area, previous_p0_exp, slope_oml, intercept_oml, display, _print)
    
    return n_e, n_i, lambda_D, T_e, T_eH, hot_fraction, p0, n_i_oml, err_n_i_oml, T_e_2, n_e_2, err_T_e, err_n_e, p0_exp, plasma_potential, floating_potential

        





   
