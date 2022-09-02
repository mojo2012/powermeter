import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import List

from configuration.DeviceEntry import DeviceEntry
from configuration.HttpServerConfig import HttpServerConfig
from configuration.Listeners import Listeners


class Configuration:
    devices: List[DeviceEntry] = []

    # in seconds
    readInterval = 60
    serialPort: str
    serialPortMacAddress: str
    logLevel: str
    storageFileLocation: str

    # connector settings
    httpServer: HttpServerConfig
    listeners: Listeners

    _rootPath: str

    def __init__(self, rootPath: str, config: SimpleNamespace):
        self._rootPath = rootPath

        self.readInterval = config.readInterval
        self.serialPort = config.serialPort
        self.serialPortMacAddress = config.serialPortMacAddress
        self.logLevel = config.logLevel

        if config.listeners:
            self.listeners = Listeners(config.listeners)
        
        storageLocation: str = config.storageLocation

        if storageLocation:
            if storageLocation.startswith("."):
                storageLocation = os.path.join(self._rootPath, Path(storageLocation))

            self.storageFileLocation = str(
                Path(os.path.join(Path(storageLocation), Path("usageData.sqlite"))).resolve().absolute())

        for device in config.devices:
            self.devices.append(DeviceEntry(device.macAddress, device.name, device.category, device.master))

def readConfig(rootPath: str, configFilePath: str):
    """
    configFile must be an absolute path
    """

    configData = open(configFilePath).read()
    # configData = json.load(configFile)
    configObj = json.loads(configData, object_hook=lambda d: SimpleNamespace(**d))

    configuration = Configuration(rootPath, configObj)

    return configuration
