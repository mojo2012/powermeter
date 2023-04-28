import paho.mqtt.client as mqtt
from logging import debug

from logging import info
from logging import error

from broker.Observer import Observer
from broker.UsageData import UsageData
from configuration.DeviceEntry import DeviceEntry
from configuration.MqttClientConfig import MqttClientConfig
import json


class MqttClientObserver(Observer):

    _host: str
    _port: int
    _client: mqtt.Client

    def __init__(self, config: MqttClientConfig):
        info(f'Starting MQTT client for {config.host}:{config.port}')

        self._host = config.host
        self._port = config.port

        self._client = mqtt.Client()
        self._client.on_connect = self.onConnect
        self._client.on_message = self.onMessage

        self._client.loop_start()

        try:
            self._client.connect(self._host, self._port, 60)
        except:
            error(f'Could not connect to MQTT server {config.host}:{config.port}')


    def onUsageDataUodate(self, device: DeviceEntry, usageData: UsageData):
        debug(f'Power usage for {device.name} ({device.macAddress}): {usageData}')

        payload = {
            device: device,
            usageData: usageData
        }

        payload = json.dumps(payload, default=vars)

        self._client.publish("plugwise", payload)

    # The callback for when the client receives a CONNACK response from the server.
    def onConnect(self, client, userdata, flags, rc):
        info(f'Connected to MQTT server: result code={rc}')

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        #client.subscribe("$SYS/#")

    # The callback for when a PUBLISH message is received from the server.
    def onMessage(self, client, userdata, msg):
        #debug(f'Received MQTT message ({msg.topic}): {msg.payload}')
        pass

