from __future__ import print_function, division

import logging
import time
from argparse import ArgumentParser
from io import BytesIO

import requests
from turingarena_cli.base import BASE_PARSER
from turingarena_cli.command import Command
from turingarena_cli.evaluate import SubmissionCommand

TURINGARENA_DEFAULT_ENDPOINT = "https://api.turingarena.org/"


class CloudServerError(Exception):
    pass


class CloudCommand(Command):
    PARSER = ArgumentParser(
        description="Use TuringArena cloud infrastructure",
        parents=[BASE_PARSER],
        add_help=False,
    )
    PARSER.add_argument("--endpoint", help="cloud API endpoint")


class CloudEvaluateCommand(CloudCommand, SubmissionCommand):
    PARSER = ArgumentParser(
        description="Evaluate a submission in the cloud",
        parents=[CloudCommand.PARSER, SubmissionCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("--evaluator", "-e", help="evaluator program", default="/usr/local/bin/python -u evaluator.py")
    PARSER.add_argument("--repository", "-r", help="repository")
    PARSER.add_argument("--oid", "-i", help="commit/tree OID")

    @property
    def endpoint(self):
        if self.args.endpoint is not None:
            return self.args.endpoint
        return TURINGARENA_DEFAULT_ENDPOINT

    def _parse_files(self, files):
        default_fields = iter(self.default_fields)
        files_dict = {}
        for file in files:
            name, path = self._parse_file(file, default_fields)
            files_dict["submission[{}]".format(name)] = open(path)
        return files_dict

    def run(self):
        print("Evaluating... may take a couple of seconds")
        for event in self._evaluation_events():
            if event["type"] == "text":
                print(event["payload"], end="")
            else:
                print(event, end="")

    def _build_parameters(self):
        return {
            "evaluator_cmd": self.args.evaluator,
            "oid": self.args.oid,
            "repository[url]": self.args.repository,
        }

    def _build_files(self):
        return {
            key: (f.filename, BytesIO(f.content))
            for key, f in self.submission.items()
        }

    def _evaluation_events(self):
        url = self.endpoint + "/evaluate"

        response = requests.post(url, data=self._build_parameters(), files=self._build_files())
        logging.debug(response.request.body.decode("utf-8"))

        if response.status_code != 200:
            raise CloudServerError("Error in cloud evaluation: {}".format(response.text))

        id = response.json()["id"]
        after = None

        while True:
            page, after = self._get_evaluation_page(id, after)
            if after is None:
                break
            for event in page:
                yield event

    def _get_evaluation_page(self, id, after):
        url = self.endpoint + "/evaluation_events?evaluation={}".format(id)
        if after is not None:
            url += "&after={}".format(after)
        backoff = 200

        while True:
            response = requests.get(url)
            if response.status_code != 200:
                raise CloudServerError("Error in getting evaluation event: {}".format(response.text))

            response_json = response.json()
            logging.debug(response_json)

            end = response_json["end"]

            if end != after:
                return response_json["data"], end

            time.sleep(backoff / 1000)
            backoff *= 1.7


subparsers = CloudCommand.PARSER.add_subparsers(title="subcommand", dest="subcommand")
subparsers.required = True
subparsers.add_parser(
    "evaluate",
    parents=[CloudEvaluateCommand.PARSER],
    help=CloudEvaluateCommand.PARSER.description,
).set_defaults(Command=CloudEvaluateCommand)
