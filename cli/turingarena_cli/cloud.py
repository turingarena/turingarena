import logging
from argparse import ArgumentParser

import requests
import time

from turingarena_cli.base import BASE_PARSER
from turingarena_cli.command import Command

TURINGARENA_ENDPOINT = "https://api.turingarena.org/"


class CloudServerError(Exception):
    pass


class CloudEvaluation:
    def __init__(self, args):
        self.files = self._parse_files(args.file)
        self.data = self._build_parameters(args.pack, args.repository, args.evaluator)
        self.id = None
        self.after = -1

    @property
    def default_fields(self):
        return ["source"]

    def _parse_files(self, files):
        default_fields = iter(self.default_fields)
        files_dict = {}
        for file in files:
            name, path = self._parse_file(file, default_fields)
            files_dict[f"submission[{name}]"] = open(path)
        return files_dict


    @staticmethod
    def _parse_file(argument, default_fields):
        if ":" in argument:
            name, path = argument.split(":", 1)
        # elif "=" in argument:
        #     name, text_content = argument.split("=", 1)
        #     content = text_content.encode()
        #     filename = name + ".txt"
        else:
            path = argument
            name = next(default_fields)
        return name, path

    @staticmethod
    def _build_parameters(packs, repositories, evaluator):
        args = dict(evaluator_cmd=evaluator)
        name = "main"
        for pack in packs:
            args["packs[]"] = pack
        for repository in repositories:
            args["repositories[{}][url]".format(name)] = repository
            args["repositories[{}][type]".format(name)] = "git_clone"
            name += "_"
        return args


    def start_evaluation(self):
        url = TURINGARENA_ENDPOINT + "evaluate"
        response = requests.post(url, data=self.data, files=self.files)
        logging.debug(response.request.body.decode("utf-8"))

        if response.status_code == 200:
            self.id = response.json()["id"]
        else:
            raise CloudServerError(f"Error in cloud evaluation: {response.text}")


    def evaluation_events(self):
        if self.id is None:
            self.start_evaluation()
        backoff = 100
        while self.after is not None:
            for event in self._get_evaluation_event():
                if len(event) > 0:
                    backoff = 100
                    yield event
            time.sleep(backoff / 1000)
            backoff *= 1.5


    def _get_evaluation_event(self):
        url = TURINGARENA_ENDPOINT + "evaluation_events?evaluation={}&after={}".format(self.id, self.after)

        response = requests.get(url)

        if response.status_code == 200:
            response_json = response.json()
            logging.debug(response_json)
            self.after = response_json["end"]
            return response_json["data"]
        else:
            raise CloudServerError(f"Error in getting evaluation event: {response.text}")


class CloudCommand(Command):
    PARSER = ArgumentParser(
        description="Use TuringArena cloud infrastructure",
        parents=[BASE_PARSER],
        add_help=False,
    )
    PARSER.add_argument("--pack", "-p", action="append", help="specify problem pack ID")
    PARSER.add_argument("--repository", "-r", action="append", help="specify a repository to clone")


class CloudEvaluateCommand(CloudCommand):

    def run(self):
        print("Evaluating... may take a couple of seconds")
        evaluation = CloudEvaluation(self.args)
        for event in evaluation.evaluation_events():
            if event["type"] == "text":
                print(event["payload"], end="")
            else:
                print(event, end="")


    PARSER = ArgumentParser(
        description="Evaluate a submission in the cloud",
        parents=[CloudCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("file", help="submission file", nargs="+")
    PARSER.add_argument("--evaluator", "-e", help="evaluator program", default="/usr/local/bin/python -u evaluator.py")


subparsers = CloudCommand.PARSER.add_subparsers(title="subcommand", dest="subcommand")
subparsers.required = True
subparsers.add_parser(
    "evaluate",
    parents=[CloudEvaluateCommand.PARSER],
    help=CloudEvaluateCommand.PARSER.description,
).set_defaults(Command=CloudEvaluateCommand)
