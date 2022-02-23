#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

git submodule update --init --recursive

DIR="shared-file-format"
if [ ! -d "$DIR" ]; then
  ###  Control will jump here if $DIR does NOT exists ###
  echo "Error: ${DIR} submodule not found. Can not continue."
  exit 1
fi

pip install -r requirements.txt

PIP_LIST=$(pip list)
DOCRECSON='docrecjson'
if ! echo "$PIP_LIST" | grep -q "$DOCRECSON"; then
  echo "Error: ${DOCRECSON} seems not to be installed please verify this."
  exit 1
fi
