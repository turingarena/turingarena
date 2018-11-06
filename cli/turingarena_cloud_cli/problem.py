import json
import os
import sys
from functools import lru_cache


class Problem:
    def __init__(self, problem_directory):
        self._problem_directory = problem_directory

    @property
    def _internal_directory(self):
        return os.path.join(self._problem_directory, ".turingarena")

    @property
    def _json_files_path(self):
        return os.path.join(self._internal_directory, "files.json")

    @property
    def _json_problem_path(self):
        return os.path.join(self._internal_directory, "problem.json")

    @property
    @lru_cache(None)
    def _json_files(self):
        with open(self._json_files_path) as f:
            return json.load(f)

    @property
    @lru_cache(None)
    def _problem_parameters(self):
        with open(self._json_problem_path) as f:
            return json.load(f)

    @property
    def files(self):
        return self._json_files.items()

    @property
    def parameters(self):
        return self._problem_parameters

    def check_directory(self):
        if not os.path.exists(self._internal_directory):
            print("The directory {} not in a turingarena problem directory!".format(self._problem_directory), file=sys.stderr)
            exit(1)

