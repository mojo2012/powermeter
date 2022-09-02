class DeviceEntry:
    macAddress: str
    name: str
    category: str
    master: bool

    def __init__(self, macAddress: str, name: str, category: str, master = False):
        self.macAddress = macAddress.upper()
        self.name = name
        self.category = category
        self.master = master
