from pymodaq.control_modules.move_utility_classes import DAQ_Move_base  # base class
from pymodaq.control_modules.move_utility_classes import comon_parameters_fun, main  # common set of parameters for all actuators
from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo  # object used to send info back to the main thread
from easydict import EasyDict as edict  # type of dict

from zaber_motion.binary import Device, Connection
from zaber_motion import Units, Tools
from zaber_motion.exceptions.connection_failed_exception import ConnectionFailedException


LINEAR_UNITS = [unit for unit in Units.__members__ if 'LENGTH' in unit]
ANGULAR_UNITS = [unit for unit in Units.__members__ if 'ANGLE' in unit]
NATIVE_UNITS = [unit for unit in Units.__members__ if 'NATIVE' in unit]

ports = Tools.list_serial_ports()


class DAQ_Move_ZaberBinary(DAQ_Move_base):
    _controller_units = ''
    is_multiaxes = True  # set to True if this plugin is controlled for a multiaxis controller (with a unique communication link)
    stage_names = []  # "list of strings of the multiaxes

    params = [{'title': 'COM Port:', 'name': 'port', 'type': 'list', 'limits': ports},
              {'title': 'Device Index:', 'name': 'device_index', 'type': 'int', 'value': 1},
              {'title': 'Infos:', 'name': 'infos', 'type': 'str', 'value': ''},
              {'title': 'Units:', 'name': 'unit', 'type': 'list', 'limits': LINEAR_UNITS},
              ] + comon_parameters_fun(is_multiaxes, stage_names)

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)

    def check_position(self):
        """Get the current position from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = self.controller.get_position(Units[self.controller_units])
        pos = self.get_position_with_scaling(pos)
        self.emit_status(ThreadCommand('check_position', [pos]))
        return pos

    def close(self):
        """
        Terminate the communication protocol
        """
        try:
            self.controller.connection.close()
        except:
            pass

    def commit_settings(self, param):
        """
            | Activate any parameter changes on the PI_GCS2 hardware.
            |
            | Called after a param_tree_changed signal from DAQ_Move_main.

        """
        if param.name() == "unit":
            self.controller_units = param.value()
        else:
            pass

    def ini_stage(self, controller=None):
        try:
            self.status.update(edict(info="", controller=None, initialized=False))
            if self.settings.child('multiaxes', 'ismultiaxes').value() and self.settings.child('multiaxes',
                                   'multi_status').value() == "Slave":
                if controller is None:
                    raise Exception('no controller has been defined externally while this axe is a slave one')
                else:
                    self.controller = controller
            else:  # Master stage
                try:
                    connection = Connection.open_serial_port(self.settings['port'], 9600)
                except ConnectionFailedException:
                    raise ConnectionError('Could not connect to Zaber controller on the specified serial port.')

                self.controller = Device(connection, self.settings['device_index'])

            id = self.controller.identify()
            device_type = id.device_type

            if device_type.name == 'LINEAR':
                self.settings.child('unit').setOpts(limits=LINEAR_UNITS)
            elif device_type.name == 'ROTARY':
                self.settings.child('unit').setOpts(limits=ANGULAR_UNITS)
            else:
                self.settings.child('unit').setOpts(limits=NATIVE_UNITS)
            self.controller_units = self.settings['unit']

            infos = f"{id.name} / serial: {id.serial_number} / " \
                    f"firmware: {id.firmware_version.major}.{id.firmware_version.minor}"
            self.settings.child('infos').setValue(infos)
            self.status.info = infos
            self.status.controller = self.controller
            self.status.initialized = True
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status', [getLineInfo() + str(e), 'log']))
            self.status.info = getLineInfo() + str(e)
            self.status.initialized = False
            return self.status

    def move_Abs(self, position):
        """ Move the actuator to the absolute target defined by position

        Parameters
        ----------
        position: (float) value of the absolute target positioning
        """

        position = self.check_bound(position)  #if user checked bounds, the defined bounds are applied here
        position = self.set_position_with_scaling(position)  # apply scaling if the user specified one

        self.controller.move_absolute(position, Units[self.controller_units])
        self.target_position = position

    def move_Rel(self, position):
        """ Move the actuator to the relative target actuator value defined by position

        Parameters
        ----------
        position: (flaot) value of the relative target positioning
        """
        position = self.check_bound(self.current_position+position)-self.current_position
        self.target_position = position + self.current_position

        self.controller.move_relative(position, Units[self.controller_units])

    def move_Home(self):
        self.controller.home(Units[self.controller_units])

    def stop_motion(self):
        """
        Call the specific move_done function (depending on the hardware).

        See Also
        --------
        move_done
        """

        self.controller.stop(Units[self.controller_units])
        self.move_done()  # to let the interface know the actuator stopped


if __name__ == '__main__':
    main(__file__, init=False)
