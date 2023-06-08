from typing import Dict, Union
from broker.SwitchState import SwitchState


class StatusUpdateData:

    switchState: Union[SwitchState, None] = None

    def __init__(self, dict: Dict):
        if "switchState" in dict:
            state = dict["switchState"]

            if state != None:
                if state.lower() == 'on':
                    self.switchState = SwitchState.ON
                elif state.lower() == 'off':
                    self.switchState = SwitchState.OFF