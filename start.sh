#!/bin/sh

tmux -2 -f /dev/null start-server \; source-file config.tmux
