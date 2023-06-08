import re
from types import SimpleNamespace
from typing import List, Union
import paho.mqtt.client as mqtt
from logging import debug

from logging import info
from logging import error

from broker.Observer import Observer
from broker.UsageData import UsageData
from configuration.DeviceEntry import DeviceEntry
from configuration.MqttClientConfig import MqttClientConfig
import json

from broker.Broker import Broker
from broker.StatusUpdateData import StatusUpdateData
from paho.mqtt.client import MQTTMessage

class MqttClientObserver(Observer):

    __MQTT_PATH = "smartplug/"

    __UPDATE_MESSAGE_TOPIC_PATH_REGEX = re.compile(r"smartplug\/plugwise\/([a-zA-Z0-9\.\-\_]*)\/state")

    _host: str
    _port: int
    _client: mqtt.Client

    _listeners: List[Broker]

    def __init__(self, config: MqttClientConfig, listeners: List[Broker] = []):
        info(f'Starting MQTT client for {config.host}:{config.port}')

        self._listeners = listeners

        self._host = config.host
        self._port = config.port

        self._client = mqtt.Client()
        self._client.on_connect = self.onConnect
        self._client.on_message = self.onMessage

        self._client.loop_start()

        try:
            self._client.connect(self._host, self._port, 10)
        except:
            error(f'Could not connect to MQTT server {config.host}:{config.port}')


    def onUsageDataUpdate(self, device: DeviceEntry, usageData: UsageData):
        debug(f'Power usage for {device.name} ({device.address}): {usageData}')

        if hasattr(usageData, "temperature") and usageData.temperature is not None:
            self._client.publish(self.__MQTT_PATH + device.address + "/temperature", usageData.temperature)

        if hasattr(usageData, "power") and usageData.power is not None:
            self._client.publish(self.__MQTT_PATH + device.address + "/power", usageData.power)

        if hasattr(usageData, "latestMotion") and usageData.latestMotion is not None:
            self._client.publish(self.__MQTT_PATH + device.address + "/latestMotion", usageData.latestMotion.isoformat())

        if hasattr(usageData, "switchState") and usageData.switchState is not None:
            self._client.publish(self.__MQTT_PATH + device.address + "/switchState", str(usageData.switchState))

    # The callback for when the client receives a CONNACK response from the server.
    def onConnect(self, client, userdata, flags, rc):
        info(f'Connected to MQTT server: result code={rc}')

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self._client.subscribe(topic = self.__MQTT_PATH + "#", qos = 0)

    def _consumeMessage(self, msg: MQTTMessage):
        self._client.publish(msg.topic, retain = True)

    # The callback for when a PUBLISH message is received from the server.
    def onMessage(self, client, userdata, msg: MQTTMessage):
        #debug(f'Received MQTT message ({msg.topic}): {msg.payload}')

        topic: str = msg.topic
        matches = re.match(self.__UPDATE_MESSAGE_TOPIC_PATH_REGEX, topic)

        if matches is not None and len(matches.groups()) == 1:
            data: Union[StatusUpdateData, None] = None

            try:
                if msg.payload is not None and len(msg.payload) > 0:
                    payload: SimpleNamespace = json.loads(msg.payload, object_hook=lambda d: SimpleNamespace(**d))
                    data = StatusUpdateData(payload.__dict__)

                    deviceAddress = matches.group(1)

                    for listener in self._listeners:
                        try:
                            listener.onStateUpdate(deviceAddress, data)
                        except Exception as ex:
                            error(f"Error while sending status update to device {deviceAddress}: {data}")

                    if msg.retain == 1:
                        self._consumeMessage(msg)
            except Exception as ex:
                error(f"Could not parse status update message: {msg.payload}")


