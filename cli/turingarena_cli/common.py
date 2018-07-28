from __future__ import print_function


def error(string):
    print("\033[1;31m==> ERROR:\033[0m {}".format(string))


def warning(string):
    print("\033[1;33m==> WARNING:\033[0m {}".format(string))


def ok(string):
    print("\033[1;32m==>\033[0m {}".format(string))


def info(string):
    print("\033[1;34m  ->\033[0m {}".format(string))
