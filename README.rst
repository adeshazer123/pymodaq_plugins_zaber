pymodaq_plugins_zaber (Zaber Technologies)
#############################################

PyMoDAQ plugin for positioning devices from Zaber Technologies.
The python library for these motors is freely available as a neat python package on pypi (https://pypi.org/project/zaber-motion/) - this is most appreciated and we all wish constructors would do that more often!

Authors
=======

* Romain Géneaux
* Sebastien J. Weber (sebastien.weber@cnrs.fr)


Instruments
===========

Below is the list of instruments included in this plugin

Actuators
+++++++++

* **Zaber** All motors using the Zaber ASCII Motion Library. Rotations and translations should be both supported (units should adapt to the actuator type), but I only tested translation stages so far.
* **ZaberBinary**: control of zaber actuators using the legacy binary protocol

Installation notes
==================

Zaber developped a python package called zaber_motion. It allows two communication protocols, either ASCII
(recommended one) or Binary (legacy one). However depending on your instrument and the firmware of its controller
only the binary protocol may be available. Check this using the *Zaber Console* free software.

This ZaberBinary plugin has only be tested on a T-NA Series Micro linear actuators with built-in controllers
that only has the 5.X firmware and so is only compatible with the binary protocol.


Basic Installation
++++++++++++++++++

- Install the Zaber Software and download the latest device database.
- Use the software test your connection to the device and find the correct COM port.
- Use the software to define which motors are plugged (use the box saying "Enter peripheral ID or name", and choose your device in the list)
- Close Zaber Software (otherwise the COM port will be busy)
- Use the device in pymodaq!

Tested on Windows10 with pymodaq 3.5.2 and python 3.8.8. 
Motors used for testing: 4 x LSM050A-V2T4 (linear stages), connnected using 2 x X-MCB1 (controllers). In this configuration, there are two controllers connected on two COM ports, and two motors on each of the controllers. 

Using two actuators that share the same controller 
++++++++++++++++++++++++++++++++++++++++++++++++++

To set up two axes as two independent actuators in PyMoDAQ even though they share the same controller, you need configure it as such:

* 1st axis defined as a Zaber actuator as usual, with properties in MultiAxes/"isMultiAxes = Yes", "Status = Master",  "Axis : 1"
* Then add another Zaber actuator for the 2nd axis, this time with properties in MultiAxes/"isMultiAxes = Yes", "Status = Slave",  "Axis : 2". 
* Finally, the Controller ID of the 2nd axis (in the "Main Settings" tree) needs to be changed to match the ID of the first actuator. Then they will work together and independently.
