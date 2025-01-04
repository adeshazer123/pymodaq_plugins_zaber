from zaber_motion.ascii import Connection
from zaber_motion import Units, Tools
from zaber_motion.exceptions.connection_failed_exception import ConnectionFailedException
import logging

logger = logging.getLogger(__name__)


class ZaberMultiple: 
    """ Class to define and add multiple axis to Zaber Actuators"""

    def __init__(self,
                 controller):  # DK - we do not need to add controller as an attribute unless we want users to input
        self.controller = None
        self.axis = []
        self.unit = []

    def get_axis(self, axis):  # The same names of axis (= self.axis_value) and self.axis may be confusing. I would like to rename the attribute or the object name.
        """Return Zaber Actuator Axis"""
        return self.axis[axis - 1] # DK - See my comment in move_abs. This method may be redundant.

    def get_units(self, axis):
        """Return Zaber Actuator Units"""
        # DK - should we use a zaber_motion method to get the unit which may be more reliable?
        return self.unit[axis - 1]

    def connect(self, port):
        """Connect to the Zaber controller"""
        device_list = Connection.open_serial_port(port).detect_devices()
        if len(device_list) == 0:
            logger.error("No devices found")

        self.controller = device_list[0]

        for device in device_list:
            for axis in device.get_axis():
                self.axis.append(axis)
                self.unit.append(axis.get_units())

    def set_units(self, units, axis):
        """Sets the units of the Zaber actuators
            um: micrometer
            nm: nanometer
            mm: milometer
            inch: inches
            ang: angle
            """
        if units in ['um', 'nm', 'mm', 'in', 'cm', 'rad', 'deg']:
            if units == 'um':
                units = Units.LENGTH_MICROMETERS
            if units == 'nm':
                units = Units.LENGTH_NANOMETERS
            if units == 'mm':
                units = Units.LENGTH_MILLIMETERS
            if units == 'in':
                units = Units.LENGTH_INCHES
            if units == 'cm':
                units = Units.LENGTH_CENTIMETERS
            if units == 'rad':
                units = Units.ANGLE_RADIANS
            if units == 'deg':
                units = Units.ANGLE_DEGREES
        else:
            logger.error("Units not recognized")
            return
        self.unit[axis - 1] = units

    def move_abs(self, position, axis):

        if (axis > 0): # DK - axis can be 1. correct ">"
            # DK - can you check if self.controller has get_axis method? or did you want to use self.get_axis?
            axis = self.controller.get_axis(self.axis[axis - 1]) # DK - can we refactor the next line to be self.axis[axis - 1].move_absolute(position, self.unit)? Similarly, the following methods, too.
            axis.move_absolute(position, self.unit)

        else:
            logger.error("Controller is not a valid integer") # DK - this message could be "Axis is not ..." rather than controller. Same below.

    def move_relative(self, position, axis):

        if (axis > 0): # DK - axis can be 1. correct ">"
            axis = self.controller.get_axis(self.axis[axis - 1])
            axis.move_relative(position, self.unit)
        else:
            logger.error("Controller is not a valid integer")

    def home(self, axis):
        if (axis > 1): # DK - axis can be 1. correct ">"
            axis = self.controller.get_axis(self.axis[axis - 1])
            axis.home()
        else:
            logger.error("Controller is not a valid integer")

    def stop(self, axis):
        if (axis > 1): # DK - axis can be 1. correct ">"
            axis = self.controller.get_axis(self.axis[axis - 1])
            axis.stop()
        else:
            logger.error("Controller is not a valid integer")

    # DK - Add a method to get the current position to be used for get_actuator_value in daq_move.