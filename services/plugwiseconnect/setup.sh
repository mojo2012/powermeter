#!/bin/bash

if [ ! -d ".venv" ]; then
	echo "Setting up python environment"

	python3 -m venv .venv
fi

.venv/bin/pip3 install plugwise --no-deps
.venv/bin/pip3 install requests
.venv/bin/pip3 install serial
.venv/bin/pip3 install defusedxml
.venv/bin/pip3 install pyserial
.venv/bin/pip3 install serial
.venv/bin/pip3 install python-dateutil
.venv/bin/pip3 install crcmod
.venv/bin/pip3 install xmltodict
.venv/bin/pip3 install pyW215
.venv/bin/pip3 install async_timeout
.venv/bin/pip3 install semver
.venv/bin/pip3 install xmltodict
.venv/bin/pip3 install krak
.venv/bin/pip3 install sqlite_utils
.venv/bin/pip3 install paho-mqtt
