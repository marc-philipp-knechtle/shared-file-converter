#!/bin/bash

git submodule update --init --recursive

DIR="shared-file-format"
if [ ! -d "$DIR" ]; then
  ###  Control will jump here if $DIR does NOT exists ###
  echo "Error: ${DIR} submodule not found. Can not continue."
  exit 1
fi

cd shared-file-format/python || return 1
pip install -e .

PIP_LIST=$(pip list)
DOCRECSON='docrecjson'
if ! echo "$PIP_LIST" | grep -q "$DOCRECSON"; then
  echo "Error: ${DOCRECSON} seems not to be installed please verify this."
  exit 1
fi

pip install -r requirements.txt
