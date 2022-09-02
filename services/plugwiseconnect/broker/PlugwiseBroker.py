import time
from datetime import datetime, timedelta
from logging import debug, error, info, warn
from typing import Dict, List

from broker import Observer
from configuration.Configuration import Configuration
from configuration.DeviceEntry import DeviceEntry
from plugwise.api import Circle, Stick


class PlugwiseBroker:
    """
    The main server that coordinates the devices and broadcasts provides the results via HTTP and other interfaces
    """

    _config: Configuration

    _serialPort: Stick
    _registeredNodes: Dict[str, Circle] = {}
    _registeredMasterNode: Circle

    _observers: List[Observer] = []

    def __init__(self, config: Configuration):
        self._config = config

    def connectToSerialPort(self) -> bool:
        """
        Establishes the connection with the serial port device.
        If the connection failes an Exception is thrown
        """

        serialPortDeviceString = self._config.serialPort

        # the serial port is actually a string, but the Stick class is wrong here, it defines it as an int
        self._serialPort = Stick(serialPortDeviceString, self._config.serialPortMacAddress, timeout=1)  # type: ignore

        count = 0
        maxCount = 10

        while not self._serialPort.connected:
            count += 1
            time.sleep(5)
            self._serialPort.reconnect()

            if count == maxCount:
                break

        if not self._serialPort.connected:
            raise Exception(f'Could not connect to serial port device ${serialPortDeviceString}')

        status = self._serialPort.status()

        return True if status.value == 1 else False

    def connectToNodes(self):
        self._serialPort.enable_joining(True)

        for device in self._config.devices:
            try:
                config = self.createCircleConfiguration(device)
                node = Circle(device.macAddress, self._serialPort, config)
                self._registeredNodes[device.macAddress] = node

                if device.master:
                    info(f'Connnecting to master node \'{device.macAddress}\' ...')
                    self._registeredMasterNode = node
                    nodeInfo = node.get_info()
                    info(f'Connnected to master node \'{device.macAddress}\'')

                    now = datetime.utcnow() - timedelta(seconds=time.timezone)
                    node.set_circleplus_datetime(now)

                    node.set_log_interval(self._config.readInterval, True)

                if not device.master:
                    info(f'Connnecting to secondary node \'{device.macAddress}\' ...')

                    self._serialPort.join_node(device.macAddress, True)
                    time.sleep(30)
                    nodeInfo = node.get_info()

                    info(f'Connnected to secondary node \'{device.macAddress}\'')

            except Exception as ex:
                error(f'Could not connect to {device.name} ({device.macAddress}): {ex}')
                pass

        self._serialPort.enable_joining(False)

    def createCircleConfiguration(self, device: DeviceEntry):
        config = {
            "loginterval": self._config.readInterval,
            "reverse_pol": False,
            "mac": device.macAddress,
            "always_on": True,
            "production": True,
            "name": device.name,
            "category": device.category,
            "location": device.category,
            "init": device.master == True
        }

        return config

    def updateNodeState(self, node: Circle):
        try:
            if not node.online:
                try:
                    node.ping()
                except Exception as ex:
                    pass

            if node.online:
                usage = node.get_power_usage()
                device: DeviceEntry = next(filter(lambda d: d.macAddress == node.mac, self._config.devices))

                for observer in self._observers:
                    try:
                        observer.onUsageDataUodate(device, usage)
                    except Exception as ex:
                        error(f'Calling objserver {observer} failed: {str(ex)}')

                debug(f'Power usage for {node.name} ({node.mac}): {usage}')
            else:
                warn(f'Could not get power usage data from {node.name}: {node.mac}: device is offline')

        except Exception as ex:
            error(f'Could not get power usage data from {node.name}: {node.mac}: {str(ex)}')

    def registerObserver(self, observer: Observer):
        self._observers.append(observer)

    def start(self, observeNodes: bool):
        portConnected = self.connectToSerialPort()

        if portConnected:
            self.connectToNodes()

            info("Plugwise broker started")

            infosPrinted = False

            while True:
                for macAddress in self._registeredNodes.keys():
                    node: Circle = self._registeredNodes[macAddress]

                    if not infosPrinted:
                        infosPrinted = True
                        nodeInfo = node.get_info()
                        info(f'Node info for {node.name} ({node.mac}): {nodeInfo}')

                    if observeNodes:
                        self.updateNodeState(node)

                # time.sleep(self._config.readInterval)
                time.sleep(10)
