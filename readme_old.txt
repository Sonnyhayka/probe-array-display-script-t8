Hello!

Firstly, I suspect there is a power supply issue with the tower. The power button sometimes flashes orange and doesn't boot up.
Unplugging it, plugging it back in then waiting a few moments usually works but that is not a long term solution.

SULI/CCI: Before starting anything on the project I HIGHLY recommend you keep some sort of tracker to document any work done.
This will make the midpoint and final presentations much easier to do. If not familiar with the neutral beams system, 
Thesis_J_Beckers.pdf in the google drive folder "General Atomics MACE Group" is a good primer.

Visual Studio Code IDE was less laggy than Spyder, but both work fine. It does take a few moments to get it running so be patient.
All the files should be under MACE EXPERIMENT -> CONTROL -> rf_version. I've also pinned the programs/folders that are used the
most in the start menu.

To start out, the major components are:
	Vacuum System
	Mass Flow Controller for gas
	Function Generators
	RF Power Amplifier
	Wattmeter
	Matching Network
	Antenna
	Spectrometer
	Langmuir Probe
	Control Software

Vacuum system
	This consists of a roughing pump and a molecular pump. I've gotten to pressures as low as ~10^-8 Torr. I think anything 
	below the 10^-6 range is good. This biggest determining factor besides any air leaks is throttling the gate valve right
	above the molecular pump. Full open achieves the greatest vacuum but makes it difficult to maintain gas pressure.
	
	If not already running, you should draw a vacuum first. Instructions on the procedure can be found in
	the google drive under the filename CHECKLIST OF MACE OPERATION under the "Start vacuum" section.
	
	There's a cable behind the molecular pump power supply that's a bit loose. When it's bent the wrong way the solenoid 
	valve temporarily looses power and you'll hear low pressure air. It should be alright as long as you're not moving stuff 
	around too much in that area.

Mass Flow Controller 
	There are two valves that control gas flow with a few manual valves. The tanks are on the other side of the wall. The
	regulators should be adjusted to output around 20psi, the exact value doesn't matter but that's what I have the program 
	calibrated to.
	
	The flow controller valves open and close by sending a 0-5V signal (I think.) The program just sends a value, 5 for full 
	open and 0 for completely shut. Valve position to gas pressure is a fairly linear relationship. During operation, one
	valve should be set to full open and the other throttled to control pressure. Both should be shut when not in use.

	To calibrate to a specific range, you'll need to full open both valves. You can do this by running the test_flow.py 
	script. Then adjust  the aforementioned gate valve above the molecular pump to achieve the max desired gas pressure. 
	You'll need to determine the new valve position to pressure relationship which you can do be throttling to a few test 
	point, noting the actual gas pressure and determining a linear equation. This is can be done in excel. You'll then need 
	to update the valve variable in main.py for each type of shot.

	Under the IO.py there are two definitions, Press_start and Press_control. As written they will not work but they can be 
	modified if desired.
 
	Occasionally you might get an error from PyVisa, NIDAQ resource not available or something similar that interrupts the 
	communication between the python script and the valves. Resetting the kernel or even rebooting usually helps but sometimes
	even that doesn't work. It's most
	likely to occur when force-quiting while sending commands to adjust valve position. Resetting the NI Max Configuration 
	seems to be the only remedy that worked for me at this point. You can go to NI MAX app -> Devices and Interfaces. If you 
	don't see NI USB-6008 "Dev3" reset the configuration data under Tools in the menu bar. This will require rebooting. When 
	that's finished you need to return to this menu. You should see NI USB-6008 "Dev1". You can change the name back to Dev3 
	or change the code to reflect Dev1 when opening ports.

Function Generator
	This device is what sends a signal to the RF antenna. It can do a lot of different types of signal outputs. The syntax 
	used for the various commands is found under DG4000_ProgrammingGuide_EN.pdf 

	test_rf.py is a basic control script for interfacing and sending commands. It only works for the current function 
	generator that's already plugged in. To use a different one of the same model you need to find the specific address for 
	that device. After you plug it into the PC you can go to the NI MAX app. Under Devices and Interfaces it should pop up. 
	Just copy the VISA resource name and use that.

	As I have it written, the program should not exceed a 1Vpp output. Damage to the amplifier may occur if you exceed this 
	value with the output on. 

	You might notice that initial communication to the device occurs under IO.py when "Opening RIGOL DG4062 port." I also redid
	opening the visa resource in main.py I couldn't figure out why I couldn't send commands to the function generator within 
	the sin_shot definition but I could under the main program.

RF Power Amplifier
	The amount of amplification depends on the output frequency. I think the power read is the sum of forward and reverse 
	power, but I wouldn't rely on this indication too much. Use the dedicated wattmeter for power readings.
	
	Ensure all the cables are tightly screwed in before powering on and that the output for the function generator does not 
	exceed the 1 volt max. 

Wattmeter
	This is a two-in-one device that also can interface using the device software. There might be a way to use VISA or similar
	integration as the function generator, but I didn't get that far. The application is the model number, 81014. It's also on
	the desktop as a shortcut named Power Meter. On the meter itself the forward arow should point to the right and the reverse
	to the left (assuming you have the output of the amplifier connected to the forward side of the meter.)
	
	You can use the analog readout, but it's in logarthimic scale and it's much easier to see the digital output on the 
	software. Ensure that you have the wattage elements set to the right value. The values can be found on the label on the 
	elements themselves right above the indicating arrow.

Matching Network
	To match the 50ohm impedance output of the power amplifier, capacitors in parallel can be adjusted. On the box, C1 is to 
	ground and C2 is to the load. You can monitor the wattmeter software while in operation and adjust the capacitors so that
	reverse power is minimized. I've found that generally, they should be mostly out (in the clockwise direction) to lower 
	capacitance but this is highly dependent on frequency and voltage.
	
	I would avoid operating above 70W total forward and reverse power. Arcing between the fins of the capacitor is not uncommon
	and will lead to grounds. If that happens you can use a multimeter to locate the grounded fin and possible bend it into 
	shape or remove it entirely. You'll notice that quite a few fins have already been removed. Replacing them entirely with 
	appropriate capacitors or even a proper matching network would be ideal. 

Antenna
	The antenna is secured in place by a grounding bolt into the housing. It's composed of two pieces, a coiled up copper tube
	and a smaller diameter copper tube that connects to the F-type male adapter. They're connected with solder and can be 
	desoldered for removal. When installing the coil, some of the copper rubs off onto the cermaic so I wrapped a few layers 
	of Kapton tape.
	
	For removal, the antenna need to be unwound. You can probably do this two times before cold working the metal to the point
	it becomes difficult to shape back into a nice coil and will lead to kinks/breaks. There's some more copper tubing that 
	can be cut to size and crimped at the end for mounting.
	
	Future development for water cooling could be to run cooling water through the antenna coil itself.
	
Spectrometer
	A data screenshot can be taken by running main.py and clicking on spectrum. I didn't change any of the spectroscopy code.
	If while opening the main program, opening spectrometers fail, reset the device by turning it off and on manually.

Langmuir Probe
	The RF plasma is denser than that of the arc chamber operation. Additionally, RF energy also induces a potential across 
	the probe itself. These factors make the current probe unsuitable for RF operation. Designing a RF compensated probe or 
	acquiring a commercial one will be required to take meaningful measurements.

Control Software
	You should regularly create backups as you modify any software. This way you can revert to a slightly older version if you
	accidentally edit something out and you can't figure out what went wrong. I've left a backup copy on the google drive under 
	the Control folder.

	The main program is where the shot types are defined. This interacts with IO.py to implement commands and GUI.py for a 
	graphical interface. Only sin_shot is set up right now. am_shot and pm_shot can be configured almost identically to 
	sin_shot, just change the command sent to the function generator.
	
	One of the first things to do with the software should be to fix the stop button. It no longer works since converting to 
	an RF source. I had a crude workaround using a boolean variable "Terminate" in the main program. The issue is likely in 
	the stopshot definition under GUI.py

	Data logging has not been updated to the current mode of operation. MACEEXCELLOG.py and references should be updated to 
	store appropriate data. This file is written so that if a log excel file doesn't exist, a new one is created. I tested 
	deleting the excel file and running the main program. This would cause the main program to crash when it expected to log
	data.
	
	...


For any specific questions feel free to reach out at joel.hurtado314@icloud.com 
If it's been a while I may have forgotten how/why I did something but I'll be willing to help out.

