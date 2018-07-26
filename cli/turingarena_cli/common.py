from termcolor import colored


def error(string):
    print(colored("==> ERROR:", "red", attrs=["bold"]), string)


def warning(string):
    print(colored("==> WARNING:", "yellow", attrs=["bold"]), string)


def ok(string):
    print(colored("==>", "green", attrs=["bold"]), string)


def info(string):
    print(colored("  ->", "blue", attrs=["bold"]), string)
