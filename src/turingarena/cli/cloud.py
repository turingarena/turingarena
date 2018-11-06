import logging
import os
import sys
import time
from argparse import ArgumentParser

import requests

from turingarena.cli.base import BASE_PARSER
from turingarena.cli.command import Command
from turingarena.cli.evaluate import EvaluateCommand
from turingarena.evaluation.events import EvaluationEvent, EvaluationEventType

TURINGARENA_DEFAULT_ENDPOINT = "https://api.turingarena.org"


class CloudServerError(Exception):
    pass


def exponential_backoff(function, initial_backoff=0.1, backoff_factor=2):
    backoff = initial_backoff
    while True:
        res = function()
        if res is not None:
            return res

        backoff *= backoff_factor


class CloudCommand(Command):
    PARSER = ArgumentParser(
        description="Use TuringArena cloud infrastructure",
        parents=[BASE_PARSER],
        add_help=False,
    )
    PARSER.add_argument("--endpoint", help="cloud API endpoint")
    PARSER.add_argument("--repository", "-r", help="repository")
    PARSER.add_argument("--oid", "-i", help="commit/tree OID", default="FETCH_HEAD")
    PARSER.add_argument("--directory", "-d", help="specify a subdirectory inside the repository", default=".")

    @property
    def endpoint(self):
        if self.args.endpoint is not None:
            return self.args.endpoint
        return TURINGARENA_DEFAULT_ENDPOINT

    def _build_parameters(self):
        return {
            "oid": self.args.oid,
            "repository[url]": self.args.repository,
            "directory": self.args.directory,
        }


class CloudPullCommand(CloudCommand):
    PARSER = ArgumentParser(
        description="Pull TuringArena problem files",
        parents=[CloudCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("directory", help="directory where to save downloaded files")

    def _generate_files_request(self):
        url = self.endpoint + "/generate_file"
        response = requests.post(url, data=self._build_parameters(), files=dict(t=None))
        if response.status_code != 200:
            raise CloudServerError("Error calling /generate_file")
        return response.json()["id"]

    def _get_file_request(self, file_id):
        url = self.endpoint + "/get_file"
        data = dict(file=file_id)
        response = requests.post(url, data=data, files=dict(t=None))
        if response.status_code != 200:
            print(response.text)
            raise CloudServerError("Error calling /get_files id={}".format(file_id))
        return response.json()["url"]

    def _get_json_file(self, url):
        response = requests.get(url)
        return response.json()

    def _extract_files(self, json_file):
        for path, content in json_file.items():
            print("Extracting {}".format(os.path.join(self.args.directory, path)), file=sys.stderr)
            directory, filename = os.path.split(path)
            assert not os.path.isabs(directory)
            output_path = os.path.join(self.args.directory, directory)
            os.makedirs(output_path, exist_ok=True)
            with open(os.path.join(self.args.directory, directory, filename), "w") as f:
                print(content, file=f)

    def _check_dir(self):
        try:
            os.mkdir(self.args.directory)
        except FileExistsError:
            print("The directory {} already exists!".format(self.args.directory))
            exit(1)

    def run(self):
        self._check_dir()

        print("We are generating your files in the Cloud. Please wait a couple of seconds...")
        file_id = self._generate_files_request()
        url = exponential_backoff(lambda: self._get_file_request(file_id))
        json_file = self._get_json_file(url)
        self._extract_files(json_file)


class CloudEvaluateCommand(CloudCommand, EvaluateCommand):
    PARSER = ArgumentParser(
        description="Evaluate a submission in the cloud",
        parents=[CloudCommand.PARSER, EvaluateCommand.PARSER],
        add_help=False,
    )

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

        # TODO: use backoff function
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
subparsers.add_parser(
    "pull",
    parents=[CloudPullCommand.PARSER],
    help=CloudPullCommand.PARSER.description,
).set_defaults(Command=CloudPullCommand)
