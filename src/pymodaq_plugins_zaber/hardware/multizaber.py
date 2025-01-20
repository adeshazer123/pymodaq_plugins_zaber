from zaber_motion.ascii import Connection
from zaber_motion import Units, Tools
from zaber_motion.exceptions.connection_failed_exception import ConnectionFailedException
import logging

logger = logging.getLogger(__name__)


class ZaberMultiple: 
    """ Class to define and add multiple axis to Zaber Actuators"""

    def __init__(self):  
        self.controller = []
        self.controller_axis = []
        self.unit = []
        self.stage_type = []

    def get_axis(self, axis):  # The same names of axis (= self.axis_value) and self.axis may be confusing. I would like to rename the attribute or the object name.
        """Return Zaber Actuator Axis"""
        return self.controller_axis[axis - 1] # DK - See my comment in move_abs. This method may be redundant.

    def get_units(self, axis):
        """Return Zaber Actuator Units"""
        # DK - should we use a zaber_motion method to get the unit which may be more reliable?
        return self.unit[axis - 1]

    def connect(self, port):
        """Connect to the Zaber controller"""
        device_list = Connection.open_serial_port(port).detect_devices()
        if len(device_list) == 0:
            logger.error("No devices found")

        for i, device in enumerate(device_list):
            i += 1
            # self.controller.append(device)
            axis_control = device.get_axis(1)
            self.controller_axis.append(axis_control)
            axis_type = str(axis_control.axis_type).replace("AxisType.", "")
            self.stage_type.append(axis_type)
            self.unit.append('')
            if axis_control.axis_type.value == 1:
                self.set_units('um', i)
            elif axis_control.axis_type.value == 2: 
                self.set_units('deg', i)

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
                units = Units.LENGTH_MICROMETRES
            if units == 'nm':
                units = Units.LENGTH_NANOMETRES
            if units == 'mm':
                units = Units.LENGTH_MILLIMETRES
            if units == 'in':
                units = Units.LENGTH_INCHES
            if units == 'cm':
                units = Units.LENGTH_CENTIMETRES
            if units == 'rad':
                units = Units.ANGLE_RADIANS
            if units == 'deg':
                units = Units.ANGLE_DEGREES
        else:
            logger.error("Units not recognized")

        self.unit[axis-1] = units

    def move_abs(self, position, axis):

        if (axis > 0):
            axes = self.controller_axis[axis-1]            
            axes.move_absolute(position, self.unit[axis-1])

        else:
            logger.error("Axis is not a valid integer")
            
    def move_relative(self, position, axis):

        if (axis > 0): 
            axes = self.controller_axis[axis-1]
            axes.move_relative(position, self.unit[axis-1])
        else:
            logger.error("Axis is not a valid integer")
    
    def get_position(self, axis):
        if (axis > 0): 
            axes = self.controller_axis[axis-1]
            return axes.get_position(self.unit[axis-1])
        
        else:
            logger.error("Axis is not a valid integer")

    def home(self, axis):
        if (axis > 0): 
            axes = self.controller_axis[axis-1]
            axes.home()
        else:
            logger.error("Controller is not a valid integer")

    def stop(self, axis):
        if (axis > 0): 
            axes = self.controller_axis[axis-1]
            axes.stop()
        else:
            logger.error("Controller is not a valid integer")
            
    def stage_name(self,axis): 
       return self.stage_type[axis-1]
    
    def update_axis(self, axis): 
        if self.stage_name == 'Linear':
            self.co
