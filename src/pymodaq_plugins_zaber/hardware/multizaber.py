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
        self.unit_object = None
        self.stage_type = []

    def get_axis(self, axis):  # The same names of axis (= self.axis_value) and self.axis may be confusing. I would like to rename the attribute or the object name.
        """Return Zaber Actuator Axis"""
        return self.controller_axis[axis - 1] # DK - See my comment in move_abs. This method may be redundant.

    def get_units(self, axis):
        """Return Zaber Actuator Units"""
        # DK - should we use a zaber_motion method to get the unit which may be more reliable?'
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
                self.units_update('mm', i)
            elif axis_control.axis_type.value == 2: 
                self.units_update('degree', i)


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
            if self.unit[axis-1] == 'degree': 
                unit = 'deg'
                return axes.get_position(unit)
            
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
    
    def get_axis_object(self, axis): 
        axis = axis - 1
        return self.controller_axis[axis]
    def units_update(self, unit, axis): 

            if unit == 'mm':
                self.unit_object= Units.LENGTH_MILLIMETRES
                Units.LENGTH_MILLIMETRES
            elif unit == 'degree': # DK- deg -> what about daq_move?
                self.unit_object = Units.ANGLE_DEGREES
                Units.ANGLE_DEGREES
            elif unit == 'rad':
                self.unit_object = Units.ANGLE_RADIANS
                Units.ANGLE_RADIANS

            self.unit[axis-1] = unit
            return self.unit_object
