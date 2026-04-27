#### MACE CALIBRATION VALUES ####
"LANGMUIR PROBE"
"FLAT TOP LANGMUIR PROBE"
probeRF=0.8+0.6+0.9  # +-0.2Probe resistance (ohm)  probe + choke box + cable resistance
probeDF=0.78         #Probe diameter (mm)                        #+-0.03 #3.19
probeLF=11.1       #Probe length (mm)
probegasD=6.53 #+-0.1  #Gasket diameter
probe1in=66         #Length in the plasma

"CYLINDRICAL PROBE"
probeRC=1.0 #+_0.2
probeDC=0.95
probeLC=3.4 #+-0.1
probeCin=24


"TRANSLATABLE PROBE"
fishR=0.7 +- 0.3
fishD=0.62 + 0.02
fishL=3.72


ProbeDSS=.38 #.1
ProbeLSS=10.3 #11
ProbeRSS=30

"PROBE ARRAY"
ProbeDSSS = (3/32.0)*25.4
ProbeLSSS = 0.0
ProbeRSSS = 1.0

"PROBE IN USE!!!!!!!!!"
probeR=ProbeRSSS
probeD=ProbeDSSS
probeL=ProbeLSSS












"SPECTROMETER DATA"
f=105 #mm focal length
b0=f+0.0000001 #mm fiber distance from length
L=12.5 #mm Lens radius
d=0.6 #mm Fiber Diameter
NA=0.48 #Numerical Aperature fiber
T=5000e-06 #collection time s
PlasmaL=100 #mm Length of plasma in field of view
chamberlength=123.35  #mm +-0.1 total length of chamber

callibrationfile='labsphereCV' #file from labsphere
calcurvefile='callibrationcurve.p' #callibrated curve

relsurpress=2  #fit options gauss, surpressing peaks factor
meanavenumb=100 #fit options gauss, averaging amount of points
relfit=0.01 #fit option gauss, ignore fits below
stddevfit=0.15 #fit option gauss, standard derivation test




"TIME ADJUSTMENTS (IF NOT PROVIDED BY CONTROLLERSCRIPT AS TIMEPOINTS)"
startfiltime=0.3      #Time it takes to start the fillament supply
startarctime=0.7      #Time it takes to start the arc supply
endshottime=0      #Adjust the end of shot time
filtimeoffset=0.3  #fillament time offset
arctimeoffset=0.7  #arc time ofset



### TRANSFORMER VALUES ###




### PHYSICAL CONSTANTS ###

