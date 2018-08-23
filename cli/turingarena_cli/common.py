from __future__ import print_function


def die(message, exit_status=1):
    error(message)
    exit(exit_status)


def error(message):
    print("\033[1;31m==> ERROR:\033[0m {}".format(message))


def warning(message):
    print("\033[1;33m==> WARNING:\033[0m {}".format(message))


def ok(message):
    print("\033[1;32m==>\033[0m {}".format(message))


def info(message):
    print("\033[1;34m  ->\033[0m {}".format(message))
