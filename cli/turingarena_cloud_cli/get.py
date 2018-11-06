import json
import os
import sys

from argparse import ArgumentParser

import requests

from .problem import Problem
from .common import print_message
from .cloud import CloudCommand, CloudServerError, exponential_backoff


class GetCommand(CloudCommand):
    PARSER = ArgumentParser(
        description="Get a problem from TuringArena",
        parents=[CloudCommand.PARSER],
        add_help=False,
    )
    PARSER.add_argument("repository", help="repository")
    PARSER.add_argument("--oid", "-i", help="commit/tree OID", default="FETCH_HEAD")
    PARSER.add_argument("--directory", "-d", help="specify a subdirectory inside the repository", default=".")

    @property
    def _problem_directory(self):
        return os.path.join(os.getcwd(), os.path.basename(self.args.repository))

    @property
    def _parameters(self):
        return {
            "oid": self.args.oid,
            "repository[url]": self.args.repository,
            "directory": self.args.directory,
        }

    @property
    def _problem(self):
        return Problem(self._problem_directory)

    def _extract_file(self, path, content):
        print("Extracting {}".format(path))
        directories, filename = os.path.split(path)
        os.makedirs(os.path.join(self._problem_directory, directories), exist_ok=True)
        with open(os.path.join(self._problem_directory, path), "w") as f:
            print(content, file=f)

    def _extract_all_files(self):
        for path, content in iter(self._problem.files):
            self._extract_file(path, content)

    def _generate_files_request(self):
        url = self.endpoint + "/generate_file"
        response = requests.post(url, data=self._parameters, files=dict(t=None))
        if response.status_code != 200:
            raise CloudServerError("Error calling /generate_file")
        return response.json()["id"]

    def _get_file_request(self, file_id):
        url = self.endpoint + "/get_file"
        data = dict(file=file_id)
        for _ in exponential_backoff(initial_wait=5):
            response = requests.post(url, data=data, files=dict(t=None))
            if response.status_code != 200:
                raise CloudServerError("Error calling /get_files id={}".format(file_id))
            response_json = response.json()
            if response_json["url"] is not None:
                return response_json["url"]

    def _download_json_file(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise CloudServerError("Cannot get file {}".format(url))
        return response.text

    def _download_problem_data(self):
        request_id = self._generate_files_request()
        url = self._get_file_request(request_id)
        return self._download_json_file(url)

    def _create_directories(self):
        try:
            os.mkdir(self._problem_directory)
        except FileExistsError:
            print("Cannot create problem directory {}: file exists!".format(self._problem_directory), file=sys.stderr)
            exit(1)

    def run(self):
        self.check_repository_exists()
        self._create_directories()
        json_problem = json.dumps(self._parameters)
        with print_message("We are getting the problem from the Cloud..."):
            json_files = self._download_problem_data()
        self._problem.from_json(json_problem, json_files)
        self._extract_all_files()
