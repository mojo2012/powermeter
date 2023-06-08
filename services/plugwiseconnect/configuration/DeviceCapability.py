from enum import Enum
from typing import Union


class DeviceCapability(Enum):
	MotionSensor = "MotionSensor"
	TemperatureSensor = "TemperatureSensor"
	PowerMeter = "PowerMeter"
	PowerSwitch = "PowerSwitch"

	def forString(string: str):
		for val in DeviceCapability:
			if str(val) == string:
				return val
			
		return None