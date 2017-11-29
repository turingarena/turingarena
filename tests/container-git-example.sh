#!/usr/bin/env bash

GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p 2222" git push root@localhost:db.git HEAD:refs/heads/test
