from typing import List, Union
from configuration.DeviceType import DeviceType
from configuration.DeviceCapability import DeviceCapability, forString


class DeviceEntry:
    type: DeviceType
    address: str
    name: str
    category: str
    master: bool
    username: Union[str, None]
    password: Union[str, None]
    capabilities: List[DeviceCapability]

    def __init__(self, address: str, name: str, type: DeviceType, category: str, master=False, username = None, password = None, capabilities: List[str] = []):
        self.address = address.upper()
        self.name = name
        self.username = username
        self.password = password
        self.type = type
        self.category = category
        self.master = master
        self.capabilities = []
        
        for cap in capabilities:
            capability = forString(cap)
            
            if capability is not None:
                self.capabilities.append(capability)

    @property
    def isMotionSensor(self) -> bool:
        return DeviceCapability.MotionSensor in self.capabilities
    
    @property
    def isPowerMeter(self) -> bool:
        return DeviceCapability.PowerMeter in self.capabilities

    @property
    def isPowerSwitch(self) -> bool:
        return DeviceCapability.PowerSwitch in self.capabilities
    
    @property
    def isTemperatureSensor(self) -> bool:
        return DeviceCapability.TemperatureSensor in self.capabilities
