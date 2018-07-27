from __future__ import print_function

from termcolor import colored

quiet = False


def error(string):
    print(colored("==> ERROR:", "red", attrs=["bold"]), string)


def warning(string):
    print(colored("==> WARNING:", "yellow", attrs=["bold"]), string)


def ok(string):
    if not quiet:
        print(colored("==>", "green", attrs=["bold"]), string)


def info(string):
    if not quiet:
        print(colored("  ->", "blue", attrs=["bold"]), string)


def set_quiet():
    global quiet
    quiet = True
