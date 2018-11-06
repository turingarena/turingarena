import json
import os
import sys

from argparse import ArgumentParser
from functools import lru_cache

import requests

from .cloud import CloudCommand, CloudServerError, exponential_backoff
from .base import BASE_PARSER


class ProblemData:
    def __init__(self, json_file):
        with open(json_file) as f:
            json_data = f.read()
        self._json = json.dumps(json_data)

    @property
    def files(self):
        return self._json.items()


class GetCommand(CloudCommand):
    PARSER = ArgumentParser(
        description="Get a problem from TuringArena",
        parents=[CloudCommand.PARSER],
        add_help=False,
    )

    @property
    def _problem_directory(self):
        return os.path.join(os.getcwd(), os.path.basename(self.args.repository))

    @property
    def _internal_directory(self):
        return os.path.join(self.cwd, os.path.join(self._problem_directory, ".turingarena"))

    @property
    def _problem_data_file_path(self):
        return os.path.join(self._internal_directory, "problem.json")

    @property
    @lru_cache(None)
    def _data(self):
        return ProblemData(self._problem_data_file_path)

    def _extract_file(self, path, content):
        print("Extracting {}".format(path))
        directories, filename = os.path.split(path)
        os.makedirs(directories, exist_ok=True)
        with open(os.path.join(self._problem_directory, path), "w") as f:
            print(content, file=f)

    def _extract_all_files(self):
        for path, content in iter(self._data.files):
            self._extract_file(path, content)

    def _generate_files_request(self):
        url = self.endpoint + "/generate_file"
        response = requests.post(url, data=self.parameters, files=dict(t=None))
        if response.status_code != 200:
            raise CloudServerError("Error calling /generate_file")
        return response.json()["id"]

    def _get_file_request(self, file_id):
        url = self.endpoint + "/get_file"
        data = dict(file=file_id)
        response = requests.post(url, data=data, files=dict(t=None))
        if response.status_code != 200:
            raise CloudServerError("Error calling /get_files id={}".format(file_id))
        return response.json()["url"]

    def _download_json_file(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            raise CloudServerError("Cannot get file {}".format(url))
        with open(self._problem_data_file_path, "w") as f:
            print(response.json(), file=f)

    def _download_problem_data(self):
        request_id = self._generate_files_request()
        url = exponential_backoff(lambda: self._get_file_request(request_id))
        self._download_json_file(url)

    def _create_directories(self):
        try:
            os.mkdir(self._problem_directory)
        except FileExistsError:
            print("Cannot create problem directory {}: file exists!".format(self._problem_directory), file=sys.stderr)
            exit(1)
        os.mkdir(self._internal_directory)

    def run(self):
        assert self.repository_exists
        self._create_directories()
        self._download_problem_data()
        self._extract_all_files()
