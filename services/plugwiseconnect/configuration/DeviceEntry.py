from configuration.DeviceType import DeviceType


class DeviceEntry:
    type: DeviceType
    macAddress: str
    name: str
    category: str
    master: bool

    def __init__(self, macAddress: str, name: str, type: DeviceType, category: str, master=False):
        self.macAddress = macAddress.upper()
        self.name = name
        self.type = type
        self.category = category
        self.master = master
