import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import List

from configuration.DeviceEntry import DeviceEntry
from configuration.DeviceType import DeviceType
from configuration.HttpServerConfig import HttpServerConfig
from configuration.Listeners import Listeners


class Configuration:
    devices: List[DeviceEntry] = []

    # in seconds
    readInterval = 60
    serialPort: str
    serialPortAddress: str
    logLevel: str

    # connector settings
    httpServer: HttpServerConfig
    listeners: Listeners

    _rootPath: str

    def __init__(self, rootPath: str, config: SimpleNamespace):
        self._rootPath = rootPath

        self.readInterval = config.readInterval
        self.serialPort = config.serialPort
        self.serialPortAddress = config.serialPortMacAddress
        self.logLevel = config.logLevel

        if config.listeners:
            self.listeners = Listeners(config.listeners, rootPath)
        
        for device in config.devices:
            username = None
            password = None
            capabilities = []
            
            if hasattr(device, "password"):
                password = device.password
            if hasattr(device, "username"):
                username = device.username
            if hasattr(device, "capabilities"):
                capabilities = device.capabilities

            self.devices.append(DeviceEntry(device.address, device.name, DeviceType[device.type], device.category, device.master, username, password, capabilities))

def readConfig(rootPath: str, configFilePath: str):
    """
    configFile must be an absolute path
    """

    configData = open(configFilePath).read()
    # configData = json.load(configFile)
    configObj = json.loads(configData, object_hook=lambda d: SimpleNamespace(**d))

    configuration = Configuration(rootPath, configObj)

    return configuration
