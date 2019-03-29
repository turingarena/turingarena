import os

from collections import namedtuple

from turingarena.evallib.metadata import load_metadata
from turingarena_web.model.problem import Problem
from turingarena_web.config import config


class Contest(namedtuple("Contest", ["name"])):
    @staticmethod
    def contests():
        return [
            Contest(name)
            for name in os.listdir(config.contest_dir_path)
            if os.path.isdir(os.path.join(config.contest_dir_path, name))
        ]

    @staticmethod
    def contest(name):
        if not os.path.isdir(os.path.join(config.contest_dir_path, name)):
            return None
        return Contest(name)

    @property
    def directory(self):
        return os.path.join(config.contest_dir_path, self.name)

    @property
    def metadata(self):
        return load_metadata(self.directory).get("contest", {})

    @property
    def problems(self):
        return [
            Problem(self, name)
            for name in os.listdir(self.directory)
            if os.path.isdir(os.path.join(self.directory, name))
        ]

    @property
    def languages(self):
        return self.metadata.get("languages", [".cpp", ".c", ".java", ".py"])

    @property
    def title(self):
        return self.metadata.get("title", self.name)

    def problem(self, name):
        path = os.path.join(self.directory, name)
        if not os.path.isdir(path):
            return None
        return Problem(self, name)

    def as_json_data(self):
        return {
            "name": self.name,
            "title": self.title,
            "languages": self.languages,
            "problems": [p.name for p in self.problems]
        }
