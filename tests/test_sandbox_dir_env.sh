#!/usr/bin/env bash

make print_sandbox_dir_env
echo >&2 "Verify this prints a temporary dir name and press C-c"
taskwizard run ./print_sandbox_dir_env 2>/dev/null
