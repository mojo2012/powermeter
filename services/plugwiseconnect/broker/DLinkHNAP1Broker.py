import threading
import time
from datetime import datetime, timedelta
from logging import debug, error, info, warn
from typing import Dict, List, Union
import xml.etree.ElementTree as ET

from broker import Observer
from configuration.Configuration import Configuration
from configuration.DeviceEntry import DeviceEntry
from configuration.DeviceType import DeviceType
from pyW215.pyW215 import SmartPlug, ON, OFF
from broker.Broker import Broker
from broker.SwitchState import SwitchState
from broker.UsageData import UsageData
from broker.StatusUpdateData import StatusUpdateData

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

class DLinkHNAP1Broker(Broker):
    """
    This broker can read data from D-Link DST-W215 smart plugs and DCH-S150 motion sensors.
    """

    _registeredDevices: Dict[str, SmartPlug]

    def __init__(self, config: Configuration):
        super().__init__(config, DeviceType.DLinkHNAP1)

        self._registeredDevices = {}

        for configEntry in self.getSupportedConfigEntries():
            self.getOrCreateDevice(configEntry)

    def checkConnection(self, configEntry: DeviceEntry) -> bool:
        try:
            urlopen(f"http://{configEntry.address}", timeout=1)
        except (URLError, TimeoutError):
            return False

        return True

    def getOrCreateDevice(self, configEntry: DeviceEntry) -> Union[SmartPlug, None]:
        device = self._registeredDevices.get(configEntry.address)

        if device is None:
            result = self.checkConnection(configEntry)

            if result == True:
                username = str(configEntry.username or "")
                device = SmartPlug(configEntry.address, configEntry.password, username, False)
                self._registeredDevices[configEntry.address] = device
        
        return device

    def fetchDeviceState(self, configEntry: DeviceEntry):
        device = self.getOrCreateDevice(configEntry)

        if device is not None:
            try:
                if not device.authenticated:
                    result = self.authenticate(device)

                    if result == None or result == False:
                        warn(f"Could not fetch data from {device.model_name}: authentication failed")
                        return

                temperature = None
                switch: Union[SwitchState, None] = None
                usage = None
                latestMotion = None

                if configEntry.isMotionSensor:
                    latestMotion = self.getLatestMotionTrigger(device)
                
                if configEntry.isTemperatureSensor:
                    temperature = device.temperature

                if configEntry.isPowerSwitch:
                    if device.state == 'ON':
                        switch = SwitchState.ON
                    elif device.state == 'OFF':
                        switch = SwitchState.OFF

                if configEntry.isPowerMeter and switch is SwitchState.ON:
                    usage = device.current_consumption
                else:
                    usage = 0

                data: UsageData = UsageData(
                    unix_timestamp = time.time(), 
                    power = usage, 
                    temperature = temperature, 
                    switchState = switch,
                    latestMotion = latestMotion
                )

                return data

            except Exception as ex:
                error(f'Could not get usage data from {configEntry.name}: {configEntry.address}: {str(ex)}')
        else:
            warn(f"Device {configEntry.name} ({configEntry.address}) not reachable")

    def authenticate(self, device: SmartPlug) -> bool:
        # reset error state, which sometimes seems to stick and then no further communication is possible
        device._error_report = False
        return device.auth() is not None

    def isDeviceReady(self, device: SmartPlug):
        try:
            self.authenticate(device)
            result = device.SOAPAction('IsDeviceReady', 'IsDeviceReadyResult')

            return result == "OK"
        except:
            raise ValueError("Could not check if device is ready")
        
    def getLatestMotionTrigger(self, device: SmartPlug) -> Union[datetime, None]:
        try:
            self.authenticate(device)
            result = device.SOAPAction('GetLatestDetection', 'LatestDetectTime', device.moduleParameters("1"))

            if result is not None and type(result) is str:
                return datetime.fromtimestamp(int(result))
            else:
                return None
        except:
            raise ValueError("Could not fetch latest motion timestamp")
        
    def getDeviceName(self, device: SmartPlug) -> Union[str, None]:
        try:
            self.authenticate(device)
            deviceName = device.SOAPAction('GetDeviceSettings', 'DeviceName')

            return deviceName
        except:
            raise ValueError("Could not get device name")
    
    # def setDeviceName(self, device: SmartPlug, name: str):
    #     try:
    #         self.authenticate(device)
    #         result = device.SOAPAction('SetSocketSettings', 'SetSocketSettingsResult', f"<NickName>{name}</NickName>")

    #         return result == "OK"
    #     except:
    #         raise ValueError("Could not set device name")
   
    def getDateTime(self, device: SmartPlug) -> str:
        try:
            self.authenticate(device)
            time = str(device.SOAPAction('GetTimeSettings', 'CurrentTime'))
            date = str(device.SOAPAction('GetTimeSettings', 'CurrentDate'))
            timeZone = str(device.SOAPAction('GetTimeSettings', 'TimeZone')).replace("+", "").rjust(3, "0")

            isoDate = datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%m-%d')

            timeStamp = f"{isoDate}T{time}+{timeZone}"

            return timeStamp
        except:
            raise ValueError("Could not fetch date time")

    def onStateUpdate(self, deviceAddress: str, message: StatusUpdateData):
        super().onStateUpdate(deviceAddress, message)

        configEntry = self.getRegisteredDeviceConfig(deviceAddress)

        if configEntry is not None:
            device = self.getOrCreateDevice(configEntry)

            if device is not None and message is not None and message.switchState is not None:
                info(f"Switching {configEntry.name} to '{message.switchState}'")

                if message.switchState is SwitchState.ON:
                    device.state = "on"
                elif message.switchState is SwitchState.OFF:
                    device.state = "off"

    def start(self):
        super().start()

        info("D-Link broker started")


