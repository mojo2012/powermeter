import threading
import time
from datetime import datetime, timedelta
from logging import debug, error, info, warn
from typing import Dict, List

from broker import Observer
from configuration.Configuration import Configuration
from configuration.DeviceEntry import DeviceEntry
from configuration.DeviceType import DeviceType
from plugwise.api import Circle, Stick
from broker.Broker import Broker
from broker.UsageData import UsageData
from broker.StatusUpdateData import StatusUpdateData
from broker.SwitchState import SwitchState


class PlugwiseCircleBroker(Broker):
    """
    The main server that coordinates the devices and broadcasts provides the results via HTTP and other interfaces
    """

    _config: Configuration

    _serialPort: Stick
    _registeredNodes: Dict[str, Circle]
    _registeredMasterNode: Circle
    _registeredDevices: Dict[str, Circle]

    _observers: List[Observer] = []

    def __init__(self, config: Configuration):
        super().__init__(config, DeviceType.PlugwiseCircle)
        self._registeredDevices = {}
        self._registeredNodes = {}

    def connectToSerialPort(self) -> bool:
        """
        Establishes the connection with the serial port device.
        If the connection failes an Exception is thrown
        """

        serialPortDeviceString = self._config.serialPort

        # the serial port is actually a string, but the Stick class is wrong here, it defines it as an int
        self._serialPort = Stick(serialPortDeviceString, self._config.serialPortAddress, timeout=3)  # type: ignore

        count = 0
        maxCount = 3

        while not self._serialPort.connected:
            count += 1
            time.sleep(1)
            self._serialPort.reconnect()

            if count == maxCount:
                break

        if not self._serialPort.connected:
            raise Exception(f'Could not connect to serial port device ${serialPortDeviceString}')

        status = self._serialPort.status()

        return True if status.value == 1 else False

    def connectToNodes(self):
        self._serialPort.enable_joining(True)

        for device in self.getSupportedConfigEntries():
            try:
                config = self.createCircleConfiguration(device)
                node = Circle(device.address, self._serialPort, config)

                self._registeredDevices[device.address] = node

                self._registededConfigEntries[device.address] = device
                self._registeredNodes[device.address] = node

                if device.master:
                    info(f'Connnecting to master node \'{device.address}\' ...')
                    self._registeredMasterNode = node
                    nodeInfo = node.get_info()
                    info(f'Connnected to master node \'{device.address}\'')

                    now = datetime.utcnow() - timedelta(seconds=time.timezone)
                    node.set_circleplus_datetime(now)

                    node.set_log_interval(self._config.readInterval, True)

                if not device.master:
                    info(f'Connnecting to secondary node \'{device.address}\' ...')

                    self._serialPort.join_node(device.address, True)
                    time.sleep(30)
                    nodeInfo = node.get_info()

                    info(f'Connnected to secondary node \'{device.address}\'')

            except Exception as ex:
                error(f'Could not connect to {device.name} ({device.address}): {ex}')
                pass

        self._serialPort.enable_joining(False)

    def createCircleConfiguration(self, device: DeviceEntry):
        config = {
            "loginterval": self._config.readInterval,
            "reverse_pol": False,
            "mac": device.address,
            "always_on": True,
            "production": True,
            "name": device.name,
            "category": device.category,
            "location": device.category,
            "init": device.master == True
        }

        return config

    def onStateUpdate(self, deviceAddress: str, message: StatusUpdateData):
        super().onStateUpdate(deviceAddress, message)

        configEntry = self.getRegisteredDeviceConfig(deviceAddress)

        if configEntry is not None:
            device = self._registeredDevices.get(configEntry.address)

            if device is not None and message is not None and message.switchState is not None:
                info(f"Switching {configEntry.name} to '{message.switchState}'")

                if message.switchState is SwitchState.ON:
                    device.switch_on()
                elif message.switchState is SwitchState.OFF:
                    device.switch_off()

    def fetchDeviceState(self, configEntry: DeviceEntry):
        device = self._registeredDevices.get(configEntry.address)

        if device is not None:
            try:
                if not device.online:
                    try:
                        device.ping()
                    except Exception as ex:
                        pass

                if device.online:
                    usage = device.get_power_usage()
                    switchState = SwitchState.OFF

                    if device.relay_state == 'on':
                        SwitchState.ON

                    usageData = UsageData(
                        unix_timestamp = time.time(), 
                        power = usage.watts_1s,
                        switchState = switchState
                    )

                    return usageData
                else:
                    warn(f'Could not get power usage data from {device.name}: {device.mac}: device is offline')

            except Exception as ex:
                error(f'Could not get power usage data from {device.name}: {device.mac}: {str(ex)}')
        else:
            warn(f"Device {configEntry.name} ({configEntry.address}) not reachable")

    def start(self):
        super().start()

        portConnected = self.connectToSerialPort()

        if portConnected:
            connected = False

            while not connected:
                try:
                    self.connectToNodes()
                    connected = True
                except Exception as ex:
                    info(f"Failed to connect to nodes ({str(ex)}) - retrying ...")
                
                time.sleep(10)

            for macAddress in self._registeredNodes.keys():
                device: Circle = self._registeredNodes[macAddress]

                nodeInfo = device.get_info()
                info(f'Device info for {device.name} ({device.mac}): {nodeInfo}')
        
        info("Plugwise broker started")

