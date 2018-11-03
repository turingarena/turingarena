from __future__ import print_function, division

import logging
import sys
import time
from argparse import ArgumentParser

import requests
from turingarena_cli.base import BASE_PARSER
from turingarena_cli.command import Command
from turingarena_cli.evaluate import SubmissionCommand, EvaluateCommand

from turingarena_common.evaluation_events import EvaluationEvent, EvaluationEventType

TURINGARENA_DEFAULT_ENDPOINT = "https://api.turingarena.org"


class CloudServerError(Exception):
    pass


class CloudCommand(Command):
    PARSER = ArgumentParser(
        description="Use TuringArena cloud infrastructure",
        parents=[BASE_PARSER],
        add_help=False,
    )
    PARSER.add_argument("--endpoint", help="cloud API endpoint")


class CloudEvaluateCommand(CloudCommand, EvaluateCommand):
    PARSER = ArgumentParser(
        description="Evaluate a submission in the cloud",
        parents=[CloudCommand.PARSER, EvaluateCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("--repository", "-r", help="repository")
    PARSER.add_argument("--oid", "-i", help="commit/tree OID", default="FETCH_HEAD")
    PARSER.add_argument("--directory", "-d", help="specify a subdirectory inside the repository", default=".")

    @property
    def endpoint(self):
        if self.args.endpoint is not None:
            return self.args.endpoint
        return TURINGARENA_DEFAULT_ENDPOINT

    def run(self):
        if self.args.seed is not None:
            print("WARNING: --seed option not yet supported in cloud", file=sys.stderr)
        print("Evaluating... may take a couple of seconds", file=sys.stderr)
        for event in self._evaluation_events():
            if self.args.raw_output:
                print(event)
            else:
                if event.type is EvaluationEventType.TEXT:
                    print(event.payload, end="")

    def _build_parameters(self):
        return {
            "oid": self.args.oid,
            "repository[url]": self.args.repository,
            "directory": self.args.directory,
        }

    def _build_files(self):
        return {
            "submission[{}]".format(name): (f.filename, f.content)
            for name, f in self.submission.items()
        }

    def _evaluation_events(self):
        for json in self._evaluation_events_json():
            yield EvaluationEvent.from_json(json)

    def _evaluation_events_json(self):
        url = self.endpoint + "/evaluate"

        response = requests.post(url, data=self._build_parameters(), files=self._build_files())
        logging.debug(response.request.body.decode("utf-8"))

        if response.status_code != 200:
            raise CloudServerError("Error in cloud evaluation: {}".format(response.text))

        id = response.json()["id"]
        after = None

        startup_wait = 7.0
        time.sleep(startup_wait)

        while True:
            page, after = self._get_evaluation_page(id, after)
            for event in page:
                yield event
            if after is None:
                break

    def _get_evaluation_page(self, id, after):
        url = self.endpoint + "/evaluation_events?evaluation={}".format(id)
        if after is not None:
            url += "&after={}".format(after)

        initial_backoff = 0.1
        backoff_factor = 2

        backoff = initial_backoff
        while True:
            response = requests.get(url)
            if response.status_code != 200:
                raise CloudServerError("Error in getting evaluation event: {}".format(response.text))

            response_json = response.json()
            logging.debug(response_json)

            end = response_json["end"]

            if end != after:
                return response_json["data"], end

            time.sleep(backoff)
            backoff *= backoff_factor


subparsers = CloudCommand.PARSER.add_subparsers(title="subcommand", dest="subcommand")
subparsers.required = True
subparsers.add_parser(
    "evaluate",
    parents=[CloudEvaluateCommand.PARSER],
    help=CloudEvaluateCommand.PARSER.description,
).set_defaults(Command=CloudEvaluateCommand)
