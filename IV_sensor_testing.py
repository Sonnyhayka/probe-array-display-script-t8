# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 09:44:29 2024

@author: NeutralBeams2
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

Req = 25.0 # 1/Req = 1/R1 + 1/R2 where R1 = R2 = 50 Ohm
eps = 4.4271e-11
A = 0.0075*0.0035
d = 0.00032
#d = 0.00032*3
a = 0.005
b = 0.008
c = 0.0025
mu = 1.2566e-6

def v_calc(vi, fi):
    return vi/(2.0*Req*np.pi*fi*eps*A/d)

def i_calc(vi, fi):
    return vi/(2.0*mu*b*np.log(1.0 + a/c)*fi)


Freq = [3.5e6, 4.0e6, 4.5e6, 5.0e6, 5.5e6, 6.0e6, 6.5e6, 7.0e6, 7.25e6, 7.5e6, 7.7e6, 8.0e6, 8.5e6]
Vv = [219.5, 254.05, 286.35, 318.95, 352.35, 386.7, 421.7, 457.5, 473.8, 491.6, 506.5, 530.0, 567.5]
Vv = np.array(Vv)/1000.0
Vi = [70.9, 83.35, 97.7, 110.9, 124.75, 140.3, 157.15, 175.5, 185.3, 196.0, 204.7, 219.1, 245.05]
Vi = np.array(Vi)/1000.0
phi = [19.93, 20.71, 23.7, 27.28, 32.29, 34.73, 37.24, 40.58, 45.57, 47.76, 47.8, 46.01, 50.91]
#phi = [19.93, 20.71, 23.7, 27.28, 32.29, 34.73, 37.24, 40.58, 43.77, 45.42, 44.31, 46.01, 50.91]
phi = np.array(phi)*np.pi/180.0
WattPower = [47.25, 46.5, 46.5, 46.25, 46.0, 45.75, 45.75, 45.5, 45.75, 45.75, 45.75, 45.25, 45.0]
#WPm = np.array(WattPower) - 0.5
#WPp = np.array(WattPower) + 0.5

def p_calc(vv, vi, pi):
    return vv*vi*np.cos(pi)/2.0

Power = []
P_temp = []
V_tot = []
I_tot = []
i = 0
for fii in Freq:
    V_temp = v_calc(Vv[i], fii)
    I_temp = i_calc(Vi[i], fii)
    V_tot.append(V_temp)
    I_tot.append(I_temp)
    P_temp.append(V_temp*I_temp)
    Power.append(p_calc(V_temp, I_temp, phi[i]))
    i += 1

Freq = np.array(Freq)/1e6

plt.figure(figsize=(11,9))
plt.plot(Freq, Power, 'bo', label='IV Sensor Power')
#plt.axhline(y=WattPower, xmin=4e6, xmax=8e6, color='r', label='Watt Meter Power')
plt.plot(Freq, WattPower,'r-' , label='Watt Meter Power')
#plt.plot(Freq, WPp,'r--')
#plt.plot(Freq, WPm,'r--')
plt.title('Frequency Dependence of IV Sensor', fontsize=18)
plt.xlabel('Frequency [MHz]', fontsize=16)
plt.ylabel('Measured Power [Watts]', fontsize=16)
plt.ylim(0,140)
plt.legend(fontsize=16)
plt.grid()
plt.show()

plt.figure(figsize=(11,9))
plt.plot(Freq, phi*180.0/np.pi, 'bo')
plt.title('Frequency Dependence of IV Sensor Phase Shift', fontsize=18)
plt.xlabel('Frequency [MHz]', fontsize=16)
plt.ylabel('Phase Difference [deg]', fontsize=16)
plt.ylim(0,90)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

# Power Sweep at 6.5 MHz ::

Vsp = [300, 400, 500, 600, 700, 800, 900, 1000]
Vv_PS = [251.2, 336.5, 419.95, 508.0, 594.5, 676.0, 756.5, 839.5]
Vv_PS = np.array(Vv_PS)/1000.0
Vi_PS = [93.85, 123.85, 157.25, 179.55, 184.65, 159.05, 201.4, 332.65]
Vi_PS = np.array(Vi_PS)/1000.0
phi_PS = [37.53, 37.66, 38.1, 40.36, 42.1, 41.965, 32.27, 29.14]
phi_PS = np.array(phi_PS)*np.pi/180.0
WM_PS = [16.75, 28.0, 46.0, 68.5, 88.0, 107.0, 125.0, 142.0]

Power_PS = []
i = 0
for vii in Vsp:
    V_temp = v_calc(Vv_PS[i], 6.5e6)
    I_temp = i_calc(Vi_PS[i], 6.5e6)
    Power_PS.append(p_calc(V_temp, I_temp, phi_PS[i]))
    i += 1

plt.figure(figsize=(11,9))
plt.plot(Vsp, Power_PS, 'bo', label='IV Sensor Power')
#plt.axhline(y=WattPower, xmin=4e6, xmax=8e6, color='r', label='Watt Meter Power')
plt.plot(Vsp, WM_PS,'r-' , label='Watt Meter Power')
#plt.plot(Freq, WPp,'r--')
#plt.plot(Freq, WPm,'r--')
plt.title('Power Dependence of IV Sensor at 6.5 MHz', fontsize=18)
plt.xlabel('Voltage Set Point [mV]', fontsize=16)
plt.ylabel('Measured Power [Watts]', fontsize=16)
plt.ylim(0,220)
plt.legend(fontsize=16)
plt.grid()
plt.show()

'''
I_cycle, I_start = np.genfromtxt('C:\\Users\\NeutralBeams2\\Documents\\Pico_data\\current_startT.txt', delimiter=',',skip_header=1,usecols=(1,3), unpack=True)
V_cycle, V_start = np.genfromtxt('C:\\Users\\NeutralBeams2\\Documents\\Pico_data\\voltage_startT.txt', delimiter=',',skip_header=1,usecols=(1,3), unpack=True)

deltaT = abs(V_start - I_start)
F = 6.5e6
Period = 1.0/F
phase = deltaT*360.0/Period
AV_PHASE = np.average(phase)
'''

########################################################################################################

# Now applying 50 ohm terminations on oscilloscope in addition to IV sensor ::
# also realized there is a directional dependance for the sensor (follow arrow)

Freq_NEW = [3e6, 3.5e6, 4e6, 4.5e6, 5e6, 5.5e6, 6e6, 6.5e6, 7e6, 7.5e6, 8e6, 8.5e6, 9e6]
Vv_NEW = [175.3, 203.6, 233.5, 262.5, 291.8, 320.1, 349.3, 377.9, 406.0, 435.9, 464.9, 493.6, 522.8]
Vv_NEW = np.array(Vv_NEW)/(2*1000.0)
Vi_NEW = [116.9, 136.1, 157.9, 179.6, 197.1, 211.6, 234.4, 257.3, 276.7, 296.4, 314.3, 334.7, 353.4]
Vi_NEW = np.array(Vi_NEW)/(2*1000.0)
phi_NEW = [-2.723, -1.162, -1.366, -1.286, -1.034, -0.693, -0.399, -0.189, -0.517, -0.399, -0.0595, -0.0122, -0.118]
phi_NEW = np.array(phi_NEW)*np.pi/180.0
#phi_NEW = phi_NEW*0.0
WattPower_NEW = [55.0, 55.75, 56.0, 56.25, 56.6, 57.0, 57.25, 57.5, 57.75, 58.0, 58.0, 58.5, 58.5]

Power_NEW = []
i = 0
for fiii in Freq_NEW:
    V_temp = v_calc(Vv_NEW[i], fiii)
    I_temp = i_calc(Vi_NEW[i], fiii)
    #V_tot.append(V_temp)
    #I_tot.append(I_temp)
    #P_temp.append(V_temp*I_temp)
    Power_NEW.append(p_calc(V_temp, I_temp, phi[i]))
    i += 1

Freq_NEW = np.array(Freq_NEW)/1e6

plt.figure(figsize=(11,9))
plt.plot(Freq_NEW, Power_NEW, 'bo', label='IV Sensor Power')
plt.plot(Freq_NEW, np.array(Power_NEW)*3.2, 'go', label='Calibrated IV Sensor Power')
plt.plot(Freq_NEW, WattPower_NEW,'r-' , label='Watt Meter Power')
plt.title('Frequency Dependence of IV Sensor (RF Amp = 500 mVpp)', fontsize=18)
plt.xlabel('Frequency [MHz]', fontsize=16)
plt.ylabel('Measured Power [Watts]', fontsize=16)
plt.ylim(0,140)
plt.legend(fontsize=16)
plt.grid()
plt.show()

# Note: 6.02 MHz at 400 mVpp is resonant frequency for current setup (phase difference about 0 deg)


###########################################################################################################

Frequency = [3e6, 4e6, 5e6, 6e6, 7e6, 8e6, 9e6]
PWM_list = []
P_sensor_list = []

VI_list = []
VV_list = []
PHASE_list = []

aI_opt_vals = []
nI_opt_vals = []
dI_opt_vals = []

aV_opt_vals = []
nV_opt_vals = []
dV_opt_vals = []

aI_opt_err = []
nI_opt_err = []
dI_opt_err = []

aV_opt_err = []
nV_opt_err = []
dV_opt_err = []

# Frequency = 3 MHz ::

'''
Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [54.39, 59.85, 68.28, 77.66, 83.65, 94.75, 102.6, 111.9, 121.1, 129.8, 138.0]
VI = [38.08, 41.53, 47.96, 51.62, 59.34, 65.28, 70.81, 77.28, 83.71, 87.11, 94.07]
PHASE = [-1.899,-1.796, -0.743, -0.701, -0.38, -0.899, -0.07, -0.0694, -0.093, -0.222, -0.128]
PWM = [4.5, 5.0, 6.25, 8.25, 11.0, 13.75, 17.0, 20.75, 24.75, 29.0, 33.5]
'''

Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [54.4, 59.89, 68.67, 77.62, 83.96, 94.95, 103.1, 111.4, 121.2, 130.7, 137.3]
VI = [38.08, 41.53, 47.7, 51.62, 59.28, 65.15, 70.75, 77.07, 83.72, 86.9, 93.65]
PHASE = [-2.47, -1.749, -0.971, -1.021, -0.847, -1.018, -0.452, -0.28, -0.166, -0.495, -0.382]
PWM = [4.3, 5.0, 6.25, 8.2, 10.8, 13.8, 17.1, 20.75, 24.9, 29.25, 33.75]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)

P_sensor = VV*VI*np.cos(PHASE)

'''
CP = 8800.0

plt.figure(figsize=(11,9))
plt.plot(Vpp, P_sensor, 'b-', label='IV Sensor Power')
plt.plot(Vpp, P_sensor*CP, 'g-', label='Calibrated IV Sensor Power')
plt.plot(Vpp, PWM,'r-' , label='Watt Meter Power')
plt.title('Power Dependence of IV Sensor at 3 MHz', fontsize=18)
plt.xlabel('Voltage Set Point [mV]', fontsize=16)
plt.ylabel('Measured Power [Watts]', fontsize=16)
plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

plt.figure(figsize=(11,9))
plt.plot(P_sensor*CP, PWM, 'b-')
plt.title('Power Calibration of IV Sensor at 3 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()
'''

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

'''
CI = 400.0

plt.figure(figsize=(11,9))
plt.plot(Vpp, VI/25.0, 'b-', label='IV Sensor Current')
plt.plot(Vpp, VI/25.0*CI, 'g-', label='Calibrated IV Sensor Current')
plt.plot(Vpp, I_WM,'r-' , label='Watt Meter Current')
plt.title('Current of IV Sensor at 3 MHz', fontsize=18)
plt.xlabel('Voltage Set Point [mV]', fontsize=16)
plt.ylabel('Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()
'''

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

def power_func(xi, a, n, d):
    return a*xi**n + d

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.0006, 0.002, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 3 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

'''
CV = 550.0

plt.figure(figsize=(11,9))
plt.plot(Vpp, VV, 'b-', label='IV Sensor Voltage')
plt.plot(Vpp, VV*CV, 'g-', label='Calibrated IV Sensor Voltage')
plt.plot(Vpp, V_WM,'r-' , label='Watt Meter Voltage')
plt.title('Voltage of IV Sensor at 3 MHz', fontsize=18)
plt.xlabel('Voltage Set Point [mV]', fontsize=16)
plt.ylabel('Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()
'''

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.025, 0.075, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 3 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
plt.title('Power Calibration of IV Sensor at 3 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)

# Frequency = 4 MHz ::


Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [74.19, 80.83, 91.12, 104.9, 116.7, 128.3, 139.8, 152.1, 163.9, 175.6, 187.5]
VI = [49.5, 55.31, 63.33, 70.9, 78.84, 87.28, 95.0, 103.3, 111.1, 119.5, 127.2]
PHASE = [-1.177, -0.967, -0.451, -0.628, -0.692, -0.495, -0.624, -0.705, -0.736, -0.412, -0.326]
PWM = [4.25, 4.8, 6.1, 8.0, 10.75, 13.75, 17.0, 21.0, 25.0, 29.5, 33.9]

'''
Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [74.17, 81.05, 91.21, 104.4, 116.3, 127.9, 139.5, 151.9, 163.6, 175.2, 186.7]
VI = [50.02, 55.34, 63.27, 70.88, 78.82, 87.19, 95.03, 103.3, 111.3, 119.1, 127.1]
PHASE = [-0.695, -0.973, -0.261, -0.362, -0.661, -0.435, -0.559, -0.641, -0.483, -0.309, -0.499]
PWM = [4.25, 4.9, 6.2, 8.25, 10.9, 13.9, 17.3, 21.1, 25.2, 29.7, 34.1]
'''

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)    

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.0008, 0.00275, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 4 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.035, 0.1, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 4 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
plt.title('Power Calibration of IV Sensor at 4 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)

# Frequency = 4.5 MHz ::
'''
Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [81.89, 91.37, 104.0, 117.3, 130.2, 143.2, 156.2, 170.3, 183.3, 196.2, 209.1]
VI = [54.35, 62.51, 70.88, 80.23, 88.03, 98.08, 106.7, 116.3, 125.0, 134.1, 142.8]
PHASE = [-0.438, -0.788, -0.508, -0.645, -0.688, -0.874, -0.742, -0.473, -0.445, -0.405, -0.0844]
PWM = [4.25, 5.0, 6.3, 8.5, 11.0, 14.0, 17.5, 21.5, 25.5, 29.9, 34.5]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)    

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.0008, 0.003, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 4.5 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.035, 0.11, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 4.5 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

#temp_VV = power_func(VV,Va_func(4.5),Vn_func(4.5),Vd_func(4.5))
#temp_VI = power_func(VI/25.0,Ia_func(4.5),In_func(4.5),Id_func(4.5))
#temp_PS = temp_VV*temp_VI*np.cos(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
#plt.plot(temp_PS, PWM, 'ro--', label='Automated Frequency')
plt.title('Power Calibration of IV Sensor at 4.5 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

#print(max(temp_PS/PWM))
#print(min(temp_PS/PWM))

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)
'''

# Frequency = 5 MHz ::

'''
Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [91.7, 101.7, 116.3, 131.2, 145.5, 159.9, 174.2, 189.9, 204.3, 218.7, 233.4]
VI = [63.3, 69.51, 77.8, 87.66, 98.41, 108.6, 118.2, 128.9, 138.7, 148.6, 158.5]
PHASE = [-0.546, -1.058, -0.923, -0.543, -0.693, -0.717, -0.353, -0.0464, -0.158, -0.216, 0.119]
PWM = [4.2, 5.0, 6.2, 8.2, 10.9, 14.0, 17.3, 21.25, 25.4, 29.8, 34.2]
'''

Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [91.12, 101.9, 116.4, 131.2, 145.5, 160.0, 174.3, 190.3, 204.6, 219.2, 233.6]
VI = [63.08, 69.4, 78.29, 88.1, 98.56, 108.5, 118.1, 128.8, 138.6, 148.6, 158.3]
PHASE = [-0.727, -1.06, -0.801, -0.786, -0.897, -0.82, -0.414, -0.34, -0.156, -0.0116, -0.0217]
PWM = [4.25, 4.9, 6.1, 8.2, 10.75, 13.8, 17.2, 21.0, 25.25, 29.5, 34.2]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.0011, 0.0035, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 5 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.04, 0.125, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 5 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
plt.title('Power Calibration of IV Sensor at 5 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)

# Frequency = 6 MHz ::

Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [111.7, 122.0, 139.4, 156.7, 173.9, 191.4, 208.3, 227.3, 244.7, 261.6, 278.7]
VI = [76.17, 83.08, 94.88, 106.4, 118.1, 130.1, 141.7, 154.5, 166.1, 178.1, 189.5]
PHASE = [-1.294, -1.485, -1.335, -0.773, -0.461, -0.103, 0.0216, 0.164, 0.0338, 0.00795, 0.0905]
PWM = [4.2, 5.0, 6.3, 8.4, 11.0, 14.0, 17.75, 21.7, 25.8, 30.0, 34.7]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.0013, 0.00425, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 6 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.05, 0.15, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 6 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
plt.title('Power Calibration of IV Sensor at 6 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)

# Frequency = 7 MHz ::

Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [130.1, 142.2, 162.3, 182.3, 202.5, 222.7, 242.6, 264.4, 284.5, 304.7, 324.6]
VI = [88.15, 96.61, 110.2, 123.7, 137.6, 151.3, 164.9, 179.8, 193.3, 207.1, 220.6]
PHASE = [-0.622, -0.722, -0.552, -0.54, -0.505, -0.549, -0.352, -0.0273, -0.0669, 0.0464, 0.0748]
PWM = [4.2, 5.0, 6.5, 8.3, 11.25, 14.2, 17.85, 21.9, 26.0, 30.1, 35.0]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.0015, 0.00475, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 7 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.06, 0.17, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 7 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
plt.title('Power Calibration of IV Sensor at 7 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)

# Frequency = 8 MHz ::

Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [148.3, 162.3, 185.0, 208.1, 231.1, 254.1, 276.7, 301.6, 324.5, 347.2, 370.1]
VI = [100.7, 110.0, 125.5, 141.1, 156.6, 172.5, 187.7, 204.7, 220.1, 235.6, 251.1]
PHASE = [-0.73, -0.431, -0.881, -0.178, -0.251, -0.0876, -0.0512, -0.219, -0.109, -0.0423, 0.0205]
PWM = [4.4, 5.1, 6.5, 8.75, 11.4, 14.3, 17.9, 22.0, 26.0, 30.4, 35.3]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.00175, 0.0055, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 8 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.065, 0.2, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 8 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
plt.title('Power Calibration of IV Sensor at 8 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)

# Frequency = 9 MHz ::

Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [164.2, 181.4, 207.8, 233.0, 259.2, 285.9, 312.9, 339.9, 365.9, 391.7, 417.5]
VI = [109.8, 120.0, 137.0, 155.8, 174.6, 192.1, 209.0, 225.9, 244.3, 263.4, 281.9]
PHASE = [-2.074, -2.132, -1.901, -1.834, -1.578, -1.429, -1.279, -0.912, -0.643, -0.508, -0.441]
PWM = [4.3, 5.1, 6.6, 8.75, 11.4, 14.4, 18.0, 22.0, 26.1, 30.5, 35.5]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.002, 0.006, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 9 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.075, 0.225, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 9 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--')
plt.title('Power Calibration of IV Sensor at 9 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
#plt.legend(fontsize=16)
plt.grid()
plt.show()

aI_opt_vals.append(I_popt[0])
nI_opt_vals.append(I_popt[1])
dI_opt_vals.append(I_popt[2])

aV_opt_vals.append(V_popt[0])
nV_opt_vals.append(V_popt[1])
dV_opt_vals.append(V_popt[2])

aI_opt_err.append(I_popt_err[0])
nI_opt_err.append(I_popt_err[1])
dI_opt_err.append(I_popt_err[2])

aV_opt_err.append(V_popt_err[0])
nV_opt_err.append(V_popt_err[1])
dV_opt_err.append(V_popt_err[2])

PWM_list.append(PWM)
P_sensor_list.append(P_sensor_Cal)

Frequency = np.array(Frequency)/1e6
f_vals = np.linspace(3,9,num=100)

coef_Ia = np.polyfit(Frequency,aI_opt_vals,3)
coef_Va = np.polyfit(Frequency,aV_opt_vals,4)

'''
def poly_func(xi, a1, a2, a3, a4):
    return a1*xi**3 + a2*xi**2 + a3*xi + a4

popt_Ia, pcov_Ia = curve_fit(poly_func, Frequency, aI_opt_vals, p0=[10, 1, 10, 100],sigma=aI_opt_err)
'''

def Ia_func(fi):
    return coef_Ia[0]*fi**3 + coef_Ia[1]*fi**2 + coef_Ia[2]*fi + coef_Ia[3]

'''
def Ia_func(fi):
    return popt_Ia[0]*fi**3 + popt_Ia[1]*fi**2 + popt_Ia[2]*fi + popt_Ia[3]
'''

def Va_func(fi):
    return coef_Va[0]*fi**4 + coef_Va[1]*fi**3 + coef_Va[2]*fi**2 + coef_Va[3]*fi + coef_Va[4]

plt.figure(figsize=(11,9))
plt.errorbar(Frequency, aI_opt_vals, aI_opt_err, fmt='bo', capsize=3, label='Current')
plt.plot(f_vals, Ia_func(f_vals), 'k-')
plt.errorbar(Frequency, aV_opt_vals, aV_opt_err, fmt='ro', capsize=3, label='Voltage')
plt.plot(f_vals, Va_func(f_vals), 'k-')
plt.title('Frequency Calibration of IV Sensor: a', fontsize=18)
plt.xlabel('Frequency [MHz]', fontsize=16)
plt.ylabel('Calibration Coefficient (a)', fontsize=16)
plt.ylim(0,10000)
plt.legend(fontsize=16)
plt.grid()
plt.show()

coef_In = np.polyfit(Frequency,nI_opt_vals,4)
#coef_Vn = np.polyfit(Frequency,nV_opt_vals,5)
coef_Vn = np.polyfit(Frequency,nV_opt_vals,3)

def In_func(fi):
    return coef_In[0]*fi**4 + coef_In[1]*fi**3 + coef_In[2]*fi**2 + coef_In[3]*fi + coef_In[4] 
'''
def Vn_func(fi):
    return coef_Vn[0]*fi**5 + coef_Vn[1]*fi**4 + coef_Vn[2]*fi**3 + coef_Vn[3]*fi**2 + coef_Vn[4]*fi + coef_Vn[5]
'''
def Vn_func(fi):
    return coef_Vn[0]*fi**3 + coef_Vn[1]*fi**2 + coef_Vn[2]*fi + coef_Vn[3]

plt.figure(figsize=(11,9))
plt.errorbar(Frequency, nI_opt_vals, nI_opt_err, fmt='bo', capsize=3, label='Current')
plt.plot(f_vals, In_func(f_vals), 'k-')
plt.errorbar(Frequency, nV_opt_vals, nV_opt_err, fmt='ro', capsize=3, label='Voltage')
plt.plot(f_vals, Vn_func(f_vals), 'k-')
plt.title('Frequency Calibration of IV Sensor: n', fontsize=18)
plt.xlabel('Frequency [MHz]', fontsize=16)
plt.ylabel('Calibration Coefficient (n)', fontsize=16)
plt.ylim(1,2)
plt.legend(fontsize=16)
plt.grid()
plt.show()

coef_Id = np.polyfit(Frequency,dI_opt_vals,4)
coef_Vd = np.polyfit(Frequency,dV_opt_vals,4)

def Id_func(fi):
    return coef_Id[0]*fi**4 + coef_Id[1]*fi**3 + coef_Id[2]*fi**2 + coef_Id[3]*fi + coef_Id[4] 

def Vd_func(fi):
    return coef_Vd[0]*fi**4 + coef_Vd[1]*fi**3 + coef_Vd[2]*fi**2 + coef_Vd[3]*fi + coef_Vd[4]

plt.figure(figsize=(11,9))
plt.errorbar(Frequency, dI_opt_vals, dI_opt_err, fmt='bo', capsize=3, label='Current')
plt.plot(f_vals, Id_func(f_vals), 'k-')
plt.errorbar(Frequency, dV_opt_vals, dV_opt_err, fmt='ro', capsize=3, label='Voltage')
plt.plot(f_vals, Vd_func(f_vals), 'k-')
plt.title('Frequency Calibration of IV Sensor: d', fontsize=18)
plt.xlabel('Frequency [MHz]', fontsize=16)
plt.ylabel('Calibration Coefficient (d)', fontsize=16)
plt.ylim(0,10)
plt.legend(fontsize=16)
plt.grid()
plt.show()

j = 0
plt.figure(figsize=(11,9))
for ff in Frequency:
    plt.plot(P_sensor_list[j], PWM_list[j], label='Freq ='+str(ff)+' MHz')
    j += 1
plt.title('Frequency Calibration of IV Sensor', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
plt.legend(fontsize=16)
plt.grid()
plt.show()

Power_ratios = []
j = 0
plt.figure(figsize=(11,9))
for ff in Frequency:
    temp_VV = power_func(VV_list[j],Va_func(ff),Vn_func(ff),Vd_func(ff))
    temp_VI = power_func(VI_list[j]/25.0,Ia_func(ff),In_func(ff),Id_func(ff))
    temp_PS = temp_VV*temp_VI*np.cos(PHASE_list[j])
    Power_ratios.append([min(temp_PS/PWM_list[j]),max(temp_PS/PWM_list[j])])
    plt.plot(temp_PS, PWM_list[j], label='Freq ='+str(ff)+' MHz')
    j += 1
plt.title('Full Frequency Calibration of IV Sensor', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
plt.legend(fontsize=16)
plt.grid()
plt.show()


# Frequency = 4.5 MHz ::

Vpp = [160.0, 175.0, 200.0, 225.0, 250.0, 275.0, 300.0, 325.0, 350.0, 375.0, 400.0]
VV = [81.89, 91.37, 104.0, 117.3, 130.2, 143.2, 156.2, 170.3, 183.3, 196.2, 209.1]
VI = [54.35, 62.51, 70.88, 80.23, 88.03, 98.08, 106.7, 116.3, 125.0, 134.1, 142.8]
PHASE = [-0.438, -0.788, -0.508, -0.645, -0.688, -0.874, -0.742, -0.473, -0.445, -0.405, -0.0844]
PWM = [4.25, 5.0, 6.3, 8.5, 11.0, 14.0, 17.5, 21.5, 25.5, 29.9, 34.5]

VV = np.array(VV)/2000.0
VI = np.array(VI)/2000.0
PHASE = np.array(PHASE)*np.pi/180.0
PWM = np.array(PWM)    

I_WM = np.sqrt(PWM)/np.sqrt(50.0)
V_WM = np.sqrt(PWM)*np.sqrt(50.0)

#I_errors = I_WM*0.1
I_errors = I_WM*np.linspace(0.1, 0.05, num=len(I_WM))

I_popt, I_pcov = curve_fit(power_func, VI/25.0, I_WM, p0=[1000.0, 1.0, 0.1],sigma=I_errors)
I_popt_err = np.sqrt(np.diag(I_pcov))
I_vals = np.linspace(0.0008, 0.003, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VI/25.0, I_WM, yerr=I_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(I_vals, power_func(I_vals, I_popt[0], I_popt[1], I_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Current Calibration at 4.5 MHz', fontsize=18)
plt.xlabel('IV Sensor Current [Amps]', fontsize=16)
plt.ylabel('Watt Meter Current [Amps]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

#V_errors = V_WM*0.1
V_errors = V_WM*np.linspace(0.1, 0.05, num=len(V_WM))

V_popt, V_pcov = curve_fit(power_func, VV, V_WM, p0=[1000.0, 1.0, 0.1],sigma=V_errors)
V_popt_err = np.sqrt(np.diag(V_pcov))
V_vals = np.linspace(0.035, 0.11, num=100)

plt.figure(figsize=(11,9))
plt.errorbar(VV, V_WM, yerr=V_errors,fmt='bo', capsize=3, label='IV Sensor/Watt Meter Data')
plt.plot(V_vals, power_func(V_vals, V_popt[0], V_popt[1], V_popt[2]), 'r-' ,label='Calibration Fit')
plt.title('Voltage Calibration at 4.5 MHz', fontsize=18)
plt.xlabel('IV Sensor Voltage [Volts]', fontsize=16)
plt.ylabel('Watt Meter Voltage [Volts]', fontsize=16)
#plt.ylim(0,50)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print('Current Calibration [a*I^n + d] ::')
print('a = ', round(I_popt[0],3))
print('n = ', round(I_popt[1],3))
print('d = ', round(I_popt[2],3))
print()
print('Voltage Calibration [a*V^n + d] ::')
print('a = ', round(V_popt[0],3))
print('n = ', round(V_popt[1],3))
print('d = ', round(V_popt[2],3))

P_sensor_Cal = power_func(VV, V_popt[0], V_popt[1], V_popt[2])*power_func(VI/25.0, I_popt[0], I_popt[1], I_popt[2])*np.cos(PHASE)
VI_list.append(VI)
VV_list.append(VV)
PHASE_list.append(PHASE)

temp_VV = power_func(VV,Va_func(4.5),Vn_func(4.5),Vd_func(4.5))
temp_VI = power_func(VI/25.0,Ia_func(4.5),In_func(4.5),Id_func(4.5))
temp_PS = temp_VV*temp_VI*np.cos(PHASE)

plt.figure(figsize=(11,9))
plt.plot(P_sensor_Cal, PWM, 'bo--', label='Isolated Frequency')
plt.plot(temp_PS, PWM, 'ro--', label='Automated Frequency')
plt.title('Power Calibration of IV Sensor at 4.5 MHz', fontsize=18)
plt.xlabel('IV Sensor Measured Power [Watts]', fontsize=16)
plt.ylabel('Watt Meter Measured Power [Watts]', fontsize=16)
plt.ylim(0,40)
plt.legend(fontsize=16)
plt.grid()
plt.show()

print(max(temp_PS/PWM))
print(min(temp_PS/PWM))

# Function that takes Oscilloscope data from IV sensor and outputs measured power in Watts ::
    
def Calculate_Power(vv, vi, pii, fi):
    tempVS = vv/2000.0
    tempIS = vi/2000.0
    tempVV = power_func(tempVS, Va_func(fi), Vn_func(fi), Vd_func(fi))
    tempVI = power_func(tempIS/25.0, Ia_func(fi), In_func(fi), Id_func(fi))
    return tempVV*tempVI*np.cos(pii*np.pi/180.0)


