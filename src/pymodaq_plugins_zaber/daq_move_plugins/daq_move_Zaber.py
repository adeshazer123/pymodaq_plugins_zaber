
# from pymodaq.control_modules.move_utility_classes import DAQ_Move_base  # base class
# from pymodaq.control_modules.move_utility_classes import comon_parameters_fun, main  # common set of parameters for all actuators
from typing import Union, List, Dict



"""
Update Epsilon parameter in the commit_Settings to change based on the units
Change units to be infinity because we don't know the amount of stages
Update _axis_names to dictionary
Look at rest of code to ploish it"""


from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, main, DataActuatorType,\
    DataActuator  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo
from pymodaq.utils.parameter import Parameter
# from easydict import EasyDict as edict  # type of dict
from zaber_motion.ascii import Connection
from zaber_motion import Units, Tools
from zaber_motion.exceptions.connection_failed_exception import ConnectionFailedException
from pymodaq_plugins_zaber.hardware.multizaber import ZaberMultiple

import logging
logger = logging.getLogger(__name__)
logger.info("before class DAQ_Move_Zaber")

class DAQ_Move_Zaber(DAQ_Move_base):

    # find available COM ports
    ports = Tools.list_serial_ports()
    port = 'COM5' if 'COM5' in ports else ports[0] if len(ports) > 0 else ''
    logger.info(f"port: {port}")

    is_multiaxes = True 
    _axis_names: Union[List[str], Dict[str, int]] = {"1":1, "2":2} # DK - use device_list to populate.
    _controller_units: Union[str, List[str]] = ' ' 
    _epsilon: Union[float, List[float]] = 0.01 
    data_actuator_type = DataActuatorType.DataActuator 

    params = [{'title': 'COM Port:', 'name': 'com_port', 'type': 'list', 'limits': ports, 'value': port},
              {'title': 'Controller:', 'name': 'controller_str', 'type': 'str', 'value': ''},
              {'title': 'Stage Properties:', 'name': 'stage_properties', 'type': 'group', 'children': [
                  {'title': 'Stage Name:', 'name': 'stage_name', 'type': 'str', 'value': '', 'readonly': True},
                  {'title': 'Stage Type:', 'name': 'stage_type', 'type': 'str', 'value': '', 'readonly': True},
                  {'title': 'Units', 'name': 'units', 'type': 'list', 'limits': ['um', 'nm', 'mm', 'in', 'cm', 'rad', 'deg']  }
              ]}
              ] + comon_parameters_fun(is_multiaxes, axis_names = _axis_names, epsilon=_epsilon)
    logger.info(f"params: {params} loaded")

    def ini_attributes(self):

        # super().__init__(parent, params_state)
        self.controller = None
        logger.info("Ini attributes loaded :)")

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """

        try:
            self.ini_stage_init(slave_controller=controller)
            if self.is_master:
                self.controller = ZaberMultiple()
                self.controller.connect(self.settings.child('com_port').value())
                # self.controller.set_units(self.settings.child('units').value(), self.axis_value)
                # self.controller.stage_name(self.axis_value)
                # try:
                #     device_list = Connection.open_serial_port(self.settings.child('com_port').value()).detect_devices()
                # except ConnectionFailedException:
                #     raise ConnectionError('Could not connect to Zaber controller on the specified serial port.')

                # self.controller = device_list[0]
                # # self.axis_value, self.axis_name?
                # logger.info(f"The device has been updated {self.controller}")


            # check whether this stage is controlled by a multiaxe controller (to be defined for each plugin)
            # if multiaxes then init the controller here if Master state otherwise use external controller
            # elif self.settings.child('multiaxes', 'ismultiaxes').value() and self.settings.child('multiaxes',
            #                        'multi_status').value() == "Slave":
            #     if controller is None:
            #         raise Exception('no controller has been defined externally while this axe is a slave one')
            #     else:
            #         self.controller = controller
                    
            #
            # self.settings.child('controller_str').setValue(str(self.controller))
            # user_axis =  self.settings.child('multiaxes', 'axis').value()
            # if user_axis > self.controller.axis_count:
            #     self.settings.child('multiaxes', 'axis').setValue(1)
            #     self.emit_status(ThreadCommand('Update_Status', ['Zaber : You requested to use Axis number '+str(user_axis)+
            #                                                      ' but only '+str(self.controller.axis_count)+
            #                                                      ' are present. Defaulting to Axis number 1.', 'log']))
            # self.settings.child('multiaxes', 'axis').setLimits([*range(1,1+self.controller.axis_count)]) # add limits to axes
            # self.update_axis()

            self.status.info = "Zaber initialized"
            self.status.initialized = True
            return self.status.info, self.status.initialized

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status',[getLineInfo()+ str(e),'log']))
            info = getLineInfo()+ str(e)
            initialized = False
            return info, initialized

    def update_axis(self):
        stage_name = self.controller.stage_name(self.axis_value)
        self.settings.child('stage_properties', 'stage_name').setValue(stage_name)

        if stage_name == 'Linear': 
            self.settings.child('stage_properties', 'units').setLimits(['um', 'nm', 'mm', 'in', 'cm'])
            self.settings.child('stage_properties', 'units').setValue('mm')
            
        elif stage_name == 'OpticsRotary':
            self.settings.child('stage_properties', 'units').setLimits(['rad', 'deg'])
            self.settings.child('stage_properties','units').setValue('deg')
        

        # # Name and ID
        # self.settings.child('stage_properties', 'stage_name').setValue(
        #     axis.peripheral_name + ' (ID:' + str(axis.peripheral_id) + ')'
        # )
        # # Type
        # self.settings.child('stage_properties', 'stage_type').setValue(
        #     axis.axis_type.name
        # )
        # self.settings.child('units').setReadonly(False)
        # if axis.axis_type.value == 1:  # LINEAR
        #     self.settings.child('units').setLimits(['m', 'cm', 'mm', 'µm', 'nm', 'in'])
        #     self.settings.child('units').setValue('mm')
        #     self.unit = Units.LENGTH_MILLIMETRES

        # elif axis.axis_type.value == 2:  # ROTARY
        #     self.settings.child('units').setLimits(['deg', 'rad'])
        #     self.settings.child('units').setValue('deg')
        #     self.unit = Units.ANGLE_DEGREES


    def get_actuator_value(self):
        """Get the current position from the hardware with scaling conversion.
        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = DataActuator(data=self.controller.get_position(self.axis_value), 
                           units=self.settings.child('stage_properties', 'units').value())  # when writing your own plugin replace this line
        pos = self.get_position_with_scaling(pos)
        return pos


    def close(self):
        """
        Terminate the communication protocol
        """
        self.controller.connection.close()

    def commit_settings(self, param):
        """
            | Called after a param_tree_changed signal from DAQ_Move_main.
        """
        if param.name() == 'axis':
            self.controller.set_units(self.settings.child('stage_properties', 'units').value(), self.axis_value)
            stage_name = self.controller.stage_name(self.axis_value)
            self.settings.child('stage_properties','stage_name').setValue(stage_name)

        elif param.name() == 'units': 
            axis = self.controller.get_axis(self.axis_value)
            self.controller.set_units(self.settings.child('stage_properties', 'units'), self.axis_value)
            self.settings.child('epsilon').setValue(axis.settings.convert_from_native_units('pos', self.settings.child('epsilon').value(), self.unit))
                                           
            # axis = self.controller.get_axis(self.settings.child('multiaxes', 'axis').value())
            # self.controller.set_units(self.settings.child('stage_properties','units').value(), self.settings.child('multiaxes', 'axis').value())
            # stage_name = self.controller.stage_name(self.axis_value)
            # self.settings.child('stage_properties','stage_name').setValue(stage_name)
            # self.settings.child('epsilon').setValue(axis.settings.convert_from_native_units('pos', self.settings.child('epsilon').value(), self.unit))

        # # DK - I prefer to delete this because daq_move now has the unit feature
        # elif param.name() == 'units':
        #     axis = self.controller.get_axis(self.settings.child('multiaxes', 'axis').value())

        #     epsilon_native_units = axis.settings.convert_to_native_units(
        #         'pos', self.settings.child('epsilon').value(), self.unit)

        #     if param.value() == 'm':
        #         self.unit = Units.LENGTH_METRES
        #     elif param.value() == 'cm':
        #         self.unit = Units.LENGTH_CENTIMETRES
        #     elif param.value() == 'mm':
        #         self.unit = Units.LENGTH_MILLIMETRES
        #     elif param.value() == 'µm':
        #         self.unit = Units.LENGTH_MICROMETRES
        #     elif param.value() == 'nm':
        #         self.unit = Units.LENGTH_NANOMETRES
        #     elif param.value() == 'in':
        #         self.unit = Units.LENGTH_INCHES
        #     elif param.value() == 'deg':
        #         self.unit = Units.ANGLE_DEGREES
        #     elif param.value() == 'rad':
        #         self.unit = Units.ANGLE_RADIANS

        #     self.settings.child('epsilon').setValue(axis.settings.convert_from_native_units(
        #         'pos', epsilon_native_units, self.unit))    # Convert epsilon to new units

        #     self.check_position()

        else:
            pass

    def move_abs(self, position: DataActuator):
        """ Move the actuator to the absolute target defined by position
        Parameters
        ----------
        position: (flaot) value of the absolute target positioning
        """
        position = self.check_bound(position)   # if user checked bounds, the defined bounds are applied here
        self.target_position = position

        position = self.set_position_with_scaling(position)  # apply scaling if the user specified one
        self.controller.move_abs(position.value(), self.axis_value)
        self.update_axis()

        # axis = self.controller.get_axis(self.settings.child('multiaxes', 'axis').value())
        # try:
        #     axis.move_absolute(position, unit=self.unit)
        # except Exception as e:
        #     self.emit_status(ThreadCommand('Update_Status', [str(e)]))

        # self.poll_moving()  # start a loop to poll the current actuator value and compare it with target position

    def move_rel(self, position: DataActuator): 
        """ Move the actuator to the relative target actuator value defined by position

        Parameters
        ----------
        position: (flaot) value of the relative target positioning
        """
        position = (self.check_bound(self.current_position + position)
                - self.current_position)
        self.target_position = position + self.current_position

        # convert the user set position to the controller position if scaling
        # has been activated by user
        position = self.set_position_with_scaling(position)
        self.controller.move_relative(position.value(), self.axis_value)
        self.update_axis()
        # axis = self.controller.get_axis(self.settings.child('multiaxes', 'axis').value())

        # try:
        #     axis.move_relative(position, unit=self.unit)
        # except Exception as e:
        #     self.emit_status(ThreadCommand('Update_Status', [str(e)]))

        # self.poll_moving()
        # self.check_position()

    def move_home(self):
        """
          Send the update status thread command.
            See Also
            --------
            daq_utils.ThreadCommand
        """
        self.controller.home(self.axis_value)
        self.check_position()
        #self.emit_status(ThreadCommand('Update_Status', ['Zaber Actuator '+ self.parent.title + ' (axis '+str(self.settings.child('multiaxes', 'axis').value())+') has been homed']))
        # axis = self.controller.get_axis(self.settings.child('multiaxes', 'axis').value())
        # axis.home()
        # self.check_position()


    def stop_motion(self):
        """
        Call the specific move_done function (depending on the hardware).

        See Also
        --------
        move_done
        """
        self.controller.stop(self.axis_value)
        self.update_axis()
        #self.emit_status(ThreadCommand('Update_Status', ['Zaber Actuator '+ self.parent.title + ' (axis '+str(self.settings.child('multiaxes', 'axis').value())+') has been stopped']))
        # axis = self.controller.get_axis(self.settings.child('multiaxes', 'axis').value())
        # axis.stop()

if __name__ == '__main__':
    main(__file__)
