import sys, signal
import argparse
import logging
import os
import sys
from logging import info, debug
from pathlib import Path

try:
    from broker import PlugwiseBroker
    from configuration.Configuration import Configuration, readConfig
    from log.CustomFormatter import CustomFormatter
    from observers.HttpClientObserver import HttpClientObserver
    from observers.LoggingObserver import LoggingObserver
    from observers.MqttClientObserver import MqttClientObserver
    from observers.SqLiteStorageObserver import SqLiteStorageObserver

    ROOT_PATH = str(Path(__file__).parent.absolute())

    class PlugwiseConnect:

        plugwiseBroker: PlugwiseBroker

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
            programArguments = self.initArgParse().parse_args()
            configFileArg: str = os.path.abspath(programArguments.config[0])

            config = readConfig(ROOT_PATH, configFileArg)

            self.setupLogging(config)

            info("Starting plugwiseconnect")

            self.plugwiseBroker = PlugwiseBroker(config)

            if config.storageFileLocation:
                self.plugwiseBroker.registerObserver(SqLiteStorageObserver(config.storageFileLocation))

            if config.listeners is not None:
                if config.listeners.http is not None:
                    self.plugwiseBroker.registerObserver(HttpClientObserver(config.listeners.http))

                if config.listeners.mqtt is not None:
                    self.plugwiseBroker.registerObserver(MqttClientObserver(config.listeners.mqtt))

            self.plugwiseBroker.registerObserver(LoggingObserver())

            self.plugwiseBroker.start(True)

        def handleSigInt(self, _signal, _frame):
            info("Quitting ...")
            # self.plugwiseBroker.setEnabled(False)
            
            os.kill(os.getpid(), signal.SIGKILL)

    # starting up

    PlugwiseConnect().run()
except KeyboardInterrupt:
    debug("Keyboard interrupt: quitting ... ")
    os.kill(os.getpid(), signal.SIGKILL)

