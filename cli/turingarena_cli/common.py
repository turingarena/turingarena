from __future__ import print_function


def error(string):
    print(f"\033[1;31m==> ERROR:\033[0m {string}")


def warning(string):
    print(f"\033[1;33m==> WARNING:\033[0m {string}")


def ok(string):
    print(f"\033[1;32m==>\033[0m {string}")


def info(string):
    print(f"\033[1;34m  ->\033[0m {string}")
