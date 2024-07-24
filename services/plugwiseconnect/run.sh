#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# kill old instance
(cd $SCRIPT_DIR; kill $(cat .pid))

(cd $SCRIPT_DIR; .venv/bin/python3 __main__.py --config ./config.json)

