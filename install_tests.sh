#!/usr/bin/env bash

set -ex

turingarena protocol --name turingarena.protocol.tests.functions_valid install
turingarena protocol --name turingarena.protocol.tests.functions_valid proxy
turingarena protocol --name turingarena.protocol.tests.functions_valid skeleton
