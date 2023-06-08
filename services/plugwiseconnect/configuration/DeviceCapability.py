from enum import Enum, StrEnum
from typing import Union


class DeviceCapability(StrEnum):
	MotionSensor = "MotionSensor"
	TemperatureSensor = "TemperatureSensor"
	PowerMeter = "PowerMeter"
	PowerSwitch = "PowerSwitch"

	def forString(string: str):
		for val in DeviceCapability:
			if str(val) == string:
				return val
			
		return None