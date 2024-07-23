import argparse
import logging
import os
import sys
from logging import info
from pathlib import Path
from signal import SIGINT, signal
from time import sleep

from broker import PlugwiseBroker
from broker.DummyBroker import DummyBroker
from configuration.Configuration import Configuration, readConfig
from log.CustomFormatter import CustomFormatter
from observers.HttpClientObserver import HttpClientObserver
from observers.LoggingObserver import LoggingObserver
from observers.MqttClientObserver import MqttClientObserver
from observers.SqLiteStorageObserver import SqLiteStorageObserver

ROOT_PATH = str(Path(__file__).parent.absolute())

def initArgParse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s --config [CONFIG FILE]",
        description="Starts the plugwise connect utility",
    )

    parser.add_argument("--config", action="append")

    return parser

def setupLogging(config: Configuration):
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

def handleSignal(signal_received, frame):
    # Handle any cleanup here
    print("Stopping ...")
    exit(0)

def run():
    programArguments = initArgParse().parse_args()
    configFileArg: str = os.path.abspath(programArguments.config[0])

    config = readConfig(ROOT_PATH, configFileArg)

    setupLogging(config)

    info("Starting plugwiseconnect")

    plugwiseBroker = PlugwiseBroker(config)
    dummyBroker = DummyBroker(config)

    if config.storageFileLocation:
        plugwiseBroker.registerObserver(SqLiteStorageObserver(config.storageFileLocation))

    if config.listeners is not None:
        if config.listeners.http is not None:
            plugwiseBroker.registerObserver(HttpClientObserver(config.listeners.http))
            dummyBroker.registerObserver(HttpClientObserver(config.listeners.http))

        if config.listeners.mqtt is not None:
            plugwiseBroker.registerObserver(MqttClientObserver(config.listeners.mqtt))
            dummyBroker.registerObserver(MqttClientObserver(config.listeners.mqtt))

    plugwiseBroker.registerObserver(LoggingObserver())

    plugwiseBroker.start(True)
    dummyBroker.start(True)

    # Tell Python to run the handler() function when SIGINT is recieved
    signal(SIGINT, handleSignal)

    while True:
        sleep(0.1)


try:
    run()
except KeyboardInterrupt:
    info("Shutting down ...")
