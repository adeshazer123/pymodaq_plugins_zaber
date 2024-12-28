from zaber_motion.ascii import Connection
from zaber_motion import Units, Tools
from zaber_motion.exceptions.connection_failed_exception import ConnectionFailedException
import logging
logger = logging.getLogger(__name__)

class ZaberMultiple():
    """ Class to define and add multiple axis to Zaber Actuators"""

    def __init__(self, controller):
        self.controller = None
        self.axis = [None, None, None]
        self.unit = [None, None, None]
    def connect(self, port):
        """Connect to the Zaber controller"""
        device_list = Connection.open_serial_port(port)
        if len(device_list) == 0:
            logger.error("No devices found")
            return 
        self.controller = device_list[0]



        # index = next(i for i, item in enumerate(params) if item["name"] == "multiaxes")
    # index2 = next(i for i, item in enumerate(params[index]['children']) if item["name"] == "axis")
    # params[index]['children'][index2]['type'] = 'int'   # override type
    # params[index]['children'][index2]['value'] = 1
    # params[index]['children'][index2]['default'] = 1
    # del params[index]['children'][index2]['limits']     # need to remove limits to avoid bug
    #
    # # Override definition of units parameter to make it user-changeable
    # index = next(i for i, item in enumerate(params) if item["name"] == "units")
    # params[index]['readonly'] = False
    # params[index]['type'] = 'list'
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
        self.unit[axis -1] = units

    def move_abs(self, position, axis):

        if (axis > 1):
            axis = self.controller.get_axis(self.axis[axis-1])
            axis.move_absolute(position, self.unit)

        else:
            logger.error("Controller is not a valid integer")

    def move_relative(self, position, axis):

        if (axis > 1):
            axis = self.controller.get_axis(self.axis[axis-1])
            axis.move_relative(position, self.unit)
        else: 
            logger.error("Controller is not a valid integer")







