import logging
import os
import sys
import time
from argparse import ArgumentParser

import requests

from .cloud import CloudServerError, CloudCommand

from .evaluation_events import EvaluationEventType, EvaluationEvent


class SubmitCommand(CloudCommand):
    PARSER = ArgumentParser(
        description="Submit a solution to TuringArena",
        parents=[CloudCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("file", help="file to submit")

    def run(self):
        if not self.repository_exists:
            print("Error: repository {} does not exists!".format(self.args.repository), file=sys.stderr)
            exit(1)
        print("Evaluating... may take a couple of seconds", file=sys.stderr)
        for event in self._evaluation_events():
            if self.args.raw_output:
                print(event)
            else:
                if event.type == EvaluationEventType.TEXT:
                    print(event.payload, end="")

    @property
    def files(self):
        filename = self.args.file
        with open(filename) as f:
            content = f.read()
        return {
            "submission[source]": (os.path.basename(filename), content)
        }

    def _evaluation_events(self):
        for json in self._evaluation_events_json():
            yield EvaluationEvent.from_json(json)

    def _evaluation_events_json(self):
        url = self.endpoint + "/evaluate"

        response = requests.post(url, data=self.parameters, files=self.files)
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
