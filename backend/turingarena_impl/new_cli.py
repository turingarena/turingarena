import json


def make():
    pass


def evaluate():
    pass


def new_cli(args):
    json_args = json.loads(args[0])

    print(json_args)

    if json_args["command"] == "evaluate":
        evaluate()

    if json_args["command"] == "make":
        make()

