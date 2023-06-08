from logging import debug, error, info, warn
from abc import abstractmethod
from typing import Dict, List, Union
from broker.Observer import Observer

from configuration.DeviceEntry import DeviceEntry
from configuration.DeviceType import DeviceType
from configuration.Configuration import Configuration
from broker.StatusUpdateData import StatusUpdateData
from broker.UsageData import UsageData


class Broker:

    _config: Configuration
    _observers: List[Observer]
    _registededConfigEntries: Dict[str, DeviceEntry]
    
    supportedDeviceType: DeviceType
    started: bool

    def __init__(self, config: Configuration, deviceType: DeviceType):
        self.started = False
        self._observers = []
        self._registededConfigEntries = {}
        self.supportedDeviceType = deviceType
        self._config = config

        for deviceConfig in self.getSupportedConfigEntries():
            info(f'Registered device {deviceConfig.name} ({deviceConfig.address})')
            self._registededConfigEntries[deviceConfig.address] = deviceConfig

    @abstractmethod
    def start(self):
        if len(self.getSupportedConfigEntries()) > 0:
            self.started = True
        else:
            warn(f"Can't start broker for device type {self.supportedDeviceType}: no device configured")

    def fetchAndPublishDeviceStateUpdates(self):
         for deviceAddress in self._registededConfigEntries.keys():
            configEntry: DeviceEntry = self._registededConfigEntries[deviceAddress]
            
            usageData = self.fetchDeviceState(configEntry)

            if usageData is not None:
                debug(f'Fetched data for {configEntry.name} ({configEntry.address}): {usageData}')

                for observer in self._observers:
                    try:
                        observer.onUsageDataUpdate(configEntry, usageData)
                    except Exception as ex:
                        error(f'Calling objserver {observer} failed: {str(ex)}')



    @abstractmethod
    def fetchDeviceState(self, configEntry: DeviceEntry) -> UsageData:
        pass

    @abstractmethod
    def getSupportedConfigEntries(self) -> List[DeviceEntry]:
        supportedDevices = list(filter(lambda d: d.type == self.supportedDeviceType, self._config.devices))

        return supportedDevices
    
    @abstractmethod
    def registerObserver(self, observer: Observer):
        debug(f'Registering new observer: {observer}')
        self._observers.append(observer)

    def getRegisteredDeviceConfig(self, deviceAddress) -> Union[DeviceEntry, None]:
        if deviceAddress in self._registededConfigEntries:
            return self._registededConfigEntries[deviceAddress]
        else:
            return None

    @abstractmethod
    def onStateUpdate(self, deviceAddress: str, message: StatusUpdateData) -> None:
        debug(f"Received status update message for device {deviceAddress}: {message}")

    