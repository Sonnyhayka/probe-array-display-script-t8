# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 11:42:18 2024

@author: NeutralBeams2
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

FG_time, FG_vpp, FG_freq = np.genfromtxt('C:\\Users\\NeutralBeams2\\Documents\\MACE EXPERIMENT\\CODE\\DATA\\SHOT_DATA\\02992\\RAW_DATA\\RF_FUNC_GEN_OUTPUT_txt.txt', delimiter=',',skip_header=3,usecols=(0,1,2), unpack=True)
Watt_time, Watt_forw, Watt_rev = np.genfromtxt('C:\\Users\\NeutralBeams2\\Documents\\MACE EXPERIMENT\\CODE\\DATA\\SHOT_DATA\\02992\\RAW_DATA\\RF_WATTMETER_INPUT_txt.txt', delimiter=',',skip_header=4500, unpack=True)


plt.figure(figsize=(11,9))
plt.plot(FG_time, FG_vpp, label='FG Output')
plt.plot(Watt_time, Watt_forw, label='Watt Meter Output (250W Plug)')
plt.plot(Watt_time, Watt_rev, label='Watt Meter Output (1000W Plug)')
plt.title('Power Calibration Data', fontsize=18)
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Signal [Volts]', fontsize=16)
plt.legend(fontsize=16)
plt.tick_params(axis='both', labelsize=14)
plt.show()

Watt_time_trunc = []
Watt_forw_trunc = []
Watt_rev_trunc = []

i = 0
for wi in Watt_time:
    for_temp = Watt_forw[i]
    rev_temp = Watt_rev[i]
    if wi not in Watt_time_trunc: # and for_temp not in Watt_forw_trunc and rev_temp not in Watt_rev_trunc:
        Watt_time_trunc.append(wi)
        Watt_forw_trunc.append(for_temp)
        Watt_rev_trunc.append(rev_temp)
    i += 1

FG_time = FG_time[0:-1]
FG_vpp = FG_vpp[0:-1]

FG_time_trunc = []
FG_vpp_trunc = []

j = 0
for ti in FG_time:
    if j % 2 == 0:
        FG_time_trunc.append(ti)
        FG_vpp_trunc.append(FG_vpp[j])
    j += 1

#FG_time_trunc = FG_time_trunc[1:]
#FG_vpp_trunc = FG_vpp_trunc[1:]

plt.figure(figsize=(11,9))
plt.plot(FG_time_trunc, FG_vpp_trunc, label='FG Output')
plt.plot(Watt_time_trunc, Watt_forw_trunc, label='Watt Meter Output (250W Plug)')
plt.plot(Watt_time_trunc, Watt_rev_trunc, label='Watt Meter Output (1000W Plug)')
#plt.plot(Watt_time, Watt_forw*0.6 + 0.15, label='Watt Meter Output -- Scaled')
plt.title('Power Calibration Data', fontsize=18)
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Signal [Volts]', fontsize=16)
plt.legend(fontsize=16)
plt.tick_params(axis='both', labelsize=14)
plt.show()

time_aligned = []
Vpp_aligned = []

for ti in Watt_time_trunc:
    k = 0
    while ti > FG_time_trunc[k] and k < len(FG_time_trunc) - 1:
        k += 1
    time_aligned.append(FG_time_trunc[k])
    Vpp_aligned.append(FG_vpp_trunc[k])

print(len(Watt_time_trunc))

time_aligned = time_aligned[1:]
Vpp_aligned = Vpp_aligned[1:]
Watt_time_trunc = Watt_time_trunc[1:]
Watt_forw_trunc = Watt_forw_trunc[1:]
Watt_rev_trunc = Watt_rev_trunc[1:]

plt.figure(figsize=(11,9))
plt.plot(FG_time_trunc, FG_vpp_trunc, label='FG Output')
plt.plot(time_aligned, Vpp_aligned, label='FG Output Trimmed')
plt.plot(Watt_time_trunc, Watt_forw_trunc, label='Watt Meter Output (250W Plug)')
plt.plot(Watt_time_trunc, Watt_rev_trunc, label='Watt Meter Output (1000W Plug)')
#plt.plot(Watt_time, Watt_forw*0.6 + 0.15, label='Watt Meter Output -- Scaled')
plt.title('Power Calibration Data', fontsize=18)
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Signal [Volts]', fontsize=16)
plt.legend(fontsize=16)
plt.tick_params(axis='both', labelsize=14)
plt.show()

TIME = time_aligned[13:-6]
Vpp = Vpp_aligned[13:-6]
Watt_T = Watt_time_trunc[13:-6]
Watt_forward = Watt_forw_trunc[13:-6]
Watt_reverse = Watt_rev_trunc[13:-6]

plt.figure(figsize=(11,9))
plt.plot(FG_time_trunc, FG_vpp_trunc, label='FG Output')
plt.plot(TIME, Vpp, label='FG Output Trimmed')
plt.plot(Watt_T, Vpp, label='Watt Time Trimmed')
#plt.plot(Vpp, Watt, label='Watt Meter Output (250W Plug)')
#plt.plot(Watt_time_trunc, Watt_rev_trunc, label='Watt Meter Output (1000W Plug)')
#plt.plot(Watt_time, Watt_forw*0.6 + 0.15, label='Watt Meter Output -- Scaled')
plt.title('Power Calibration Data', fontsize=18)
plt.xlabel('Time [s]', fontsize=16)
plt.ylabel('Signal [Volts]', fontsize=16)
plt.legend(fontsize=16)
plt.tick_params(axis='both', labelsize=14)
plt.show()

TIME = TIME[0:-14]+TIME[-13:]
Vpp = Vpp[0:-14]+Vpp[-13:]
Watt_T = Watt_T[0:-14]+Watt_T[-13:]
Watt_forward = Watt_forward[0:-14]+Watt_forward[-13:]
Watt_reverse = Watt_reverse[0:-14]+Watt_reverse[-13:]

Vpp_measured = [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
Watt_forw_measured = [2.0, 5.0, 14.0, 27.0, 45.0, 64.0, 83.0, 101.0, 120.0, 139.0]
#Watt_rev_measured = [0.0, 0.0,]

Vpp_measured_rev = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
Watt_forw_measured_rev = [14.0, 27.0, 45.0, 64.0, 83.0, 101.0, 120.0, 139.0]


plt.figure(figsize=(11,9))
plt.plot(Vpp, Watt_forward, label='Watt Meter Output (250W Plug)')
plt.plot(Vpp, Watt_reverse, label='Watt Meter Output (1000W Plug)')
#plt.plot(Vpp_measured, Watt_forw_measured, label='Watt Meter Measurement')
#plt.plot(Vpp, np.array(Watt_forward)*100.0, label='Watt Meter Output -- Scaled')
plt.title('Power Calibration Data', fontsize=18)
plt.xlabel('FG Signal [Vpp]', fontsize=16)
plt.ylabel('Watt Meter Signal [Volts]', fontsize=16)
plt.legend(fontsize=16)
plt.tick_params(axis='both', labelsize=14)
plt.show()

Watt_interp = np.interp(Vpp_measured,Vpp,Watt_forward)
Watt_interp_reverse = np.interp(Vpp_measured_rev, Vpp, Watt_reverse)

def func(xi, a, n, d):
    return a*xi**n + d

popt, pcov = curve_fit(func,Watt_interp,Watt_forw_measured, p0=[10, 1.5, 0.01])
sig_data = np.linspace(0,1.4, num=500)

popt_rev, pcov_rev = curve_fit(func,Watt_interp_reverse,Watt_forw_measured_rev, p0=[10, 1.5, 5.0])
sig_data_rev = np.linspace(0,0.5, num=500)

plt.figure(figsize=(11,9))
#plt.plot(Vpp, Watt_forward, label='Watt Meter Output (250W Plug)')
#plt.plot(Vpp, Watt_reverse, label='Watt Meter Output (1000W Plug)')
#plt.plot(Vpp_measured, Watt_forw_measured, label='Watt Meter Measurement')
#plt.plot(Vpp, np.array(Watt_forward)*100.0, label='Watt Meter Output -- Scaled')
plt.plot(Watt_interp, Watt_forw_measured, label='Measured 250W')
plt.plot(Watt_interp_reverse, Watt_forw_measured_rev, label='Measured 1000W')
plt.plot(sig_data, func(sig_data, popt[0], popt[1], popt[2]), label='250 Fit')
plt.plot(sig_data_rev, func(sig_data_rev, popt_rev[0], popt_rev[1], popt_rev[2]), label='1000 Fit')
#plt.plot(Vpp_measured, Watt_interp, label='Interpolated Data')
plt.title('Power Calibration Data', fontsize=18)
plt.xlabel('Interpolated Watt Meter Signal [Volts]', fontsize=16)
plt.ylabel('Watt Meter Analog Measured [W]', fontsize=16)
plt.legend(fontsize=16)
plt.tick_params(axis='both', labelsize=14)
plt.show()

print()
print('Fit: W = A*(signal)^n + d')
print()
print('250W Probe Fitted Parameters:')
print('A =', popt[0])
print('n =', popt[1])
print('d =', popt[2])
print('1000W Probe Fitted Paramters:')
print('A =', popt_rev[0])
print('n =', popt_rev[1])
print('d =', popt_rev[2])
