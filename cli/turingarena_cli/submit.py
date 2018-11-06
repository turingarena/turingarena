import logging
import os
import sys
import time
from argparse import ArgumentParser

import requests

from .problem import Problem
from .cloud import CloudServerError, CloudCommand, exponential_backoff

from .evaluation_events import EvaluationEventType, EvaluationEvent


class SubmitCommand(CloudCommand):
    PARSER = ArgumentParser(
        description="Submit a solution to TuringArena",
        parents=[CloudCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("--directory", help="directory of the problem", default=".")
    PARSER.add_argument("--raw-output", help="show output as raw json data", action="store_true")
    PARSER.add_argument("file", help="file to submit")

    def run(self):
        self._problem.check_directory()
        print("Evaluating... may take a couple of seconds", file=sys.stderr)
        for event in self._evaluation_events():
            if self.args.raw_output:
                print(event)
            else:
                if event.type == EvaluationEventType.TEXT:
                    print(event.payload, end="")

    @property
    def _files(self):
        filename = self.args.file
        with open(filename) as f:
            content = f.read()
        return {
            "submission[source]": (os.path.basename(filename), content)
        }

    @property
    def _problem(self):
        return Problem(self.args.directory)

    def _evaluation_events(self):
        for json in self._evaluation_events_json():
            yield EvaluationEvent.from_json(json)

    def _evaluation_events_json(self):
        url = self.endpoint + "/evaluate"

        response = requests.post(url, data=self._problem.parameters, files=self._files)
        logging.debug(response.request.body.decode("utf-8"))

        if response.status_code != 200:
            raise CloudServerError("Error in cloud evaluation: {}".format(response.text))

        evaluation_id = response.json()["id"]
        after = None

        startup_wait = 7.0
        time.sleep(startup_wait)

        while True:
            page, after = self._get_evaluation_page(evaluation_id, after)
            for event in page:
                yield event
            if after is None:
                break

    def _get_evaluation_page(self, evaluation_id, after):
        url = self.endpoint + "/evaluation_events?evaluation={}".format(evaluation_id)
        if after is not None:
            url += "&after={}".format(after)

        for _ in exponential_backoff():
            response = requests.get(url)
            if response.status_code != 200:
                raise CloudServerError("Error in getting evaluation event: {}".format(response.text))

            response_json = response.json()
            logging.debug(response_json)

            end = response_json["end"]

            if end != after:
                return response_json["data"], end
