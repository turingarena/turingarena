#!/usr/bin/env bash

ssh -o ProxyCommand="socat - UNIX-CONNECT:/var/run/turingarena/test/sshd.sock" -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@localhost
