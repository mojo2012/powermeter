import time
import sys, signal
import argparse
import logging
import os
import sys
from logging import info, debug, error
from pathlib import Path
from typing import List



def registerProcessIdInFile():
    deleteProcessIdInFile()

    with open('.pid', 'w', encoding='utf-8') as pidFile:
        pidFile.write(str(os.getpid()))
        
def deleteProcessIdInFile():
    if os.path.exists(".pid"):
        os.remove(".pid")

try:
    from broker.Broker import Broker
    from broker.DLinkHNAP1Broker import DLinkHNAP1Broker
    from broker.PlugwiseCircleBroker import PlugwiseCircleBroker
    from configuration.Configuration import Configuration, readConfig
    from log.CustomFormatter import CustomFormatter
    from observers.HttpClientObserver import HttpClientObserver
    from observers.LoggingObserver import LoggingObserver
    from observers.MqttClientObserver import MqttClientObserver
    from observers.SqLiteStorageObserver import SqLiteStorageObserver

    ROOT_PATH = str(Path(__file__).parent.absolute())

    class PlugwiseConnect:

        brokers: List[Broker] = []

        def __init__(self):
            signal.signal(signal.SIGINT, self.handleSigInt)

        def initArgParse(self) -> argparse.ArgumentParser:
            parser = argparse.ArgumentParser(
                usage="%(prog)s --config [CONFIG FILE]",
                description="Starts the plugwise connect utility",
            )

            parser.add_argument("--config", action="append")

            return parser

        def setupLogging(self, config: Configuration):
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.formatter = CustomFormatter()

            logger = logging.getLogger()

            if "DEBUG" == config.logLevel:
                logger.setLevel(logging.DEBUG)
            elif "INFO" == config.logLevel:
                logger.setLevel(logging.INFO)
            elif "WARNING" == config.logLevel:
                logger.setLevel(logging.WARNING)
            elif "ERROR" == config.logLevel:
                logger.setLevel(logging.ERROR)

            logger.addHandler(streamHandler)

            pass

        def run(self):
            registerProcessIdInFile();

            programArguments = self.initArgParse().parse_args()
            configFileArg: str = os.path.abspath(programArguments.config[0])

            config = readConfig(ROOT_PATH, configFileArg)

            self.setupLogging(config)

            info("Starting plugwiseconnect")

            self.brokers.append(PlugwiseCircleBroker(config))
            self.brokers.append(DLinkHNAP1Broker(config))

            for broker in self.brokers:
                if config.listeners is not None:
                    if config.listeners.db is not None:
                        broker.registerObserver(SqLiteStorageObserver(config.listeners.db))

                    if config.listeners.http is not None:
                        broker.registerObserver(HttpClientObserver(config.listeners.http))

                    if config.listeners.mqtt is not None:
                        broker.registerObserver(MqttClientObserver(config.listeners.mqtt, self.brokers))

                broker.registerObserver(LoggingObserver())
                
                try:
                    broker.start()
                except Exception as ex:
                    error(f"Could not start broker for device type {broker.supportedDeviceType}: {str(ex)}")

            while True:
                for broker in self.brokers:
                    broker.fetchAndPublishDeviceStateUpdates()
                
                # time.sleep(config.readInterval)
                time.sleep(15)

        def handleSigInt(self, _signal, _frame):
            info("Quitting ...")
            deleteProcessIdInFile()
            os.kill(os.getpid(), signal.SIGKILL)

    # starting up

    PlugwiseConnect().run()
except KeyboardInterrupt:
    debug("Keyboard interrupt: quitting ... ")
    deleteProcessIdInFile()
    os.kill(os.getpid(), signal.SIGKILL)

