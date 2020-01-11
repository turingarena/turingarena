#!/bin/bash
# Install and run the python CLI

set -e

VENV="$PWD/.turingarena_venv"
CLI_DIR="$PWD/python-turingarena-cli/"

if ! [ -d "$VENV" ]; then
	python3 -m venv "$VENV"
	. "$VENV/bin/activate"
	(cd "$CLI_DIR" && python3 setup.py develop)
	
fi

. "$VENV/bin/activate"
exec turingarena "$@"
