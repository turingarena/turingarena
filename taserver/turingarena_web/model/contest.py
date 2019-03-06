import json
import os
from collections import namedtuple

from turingarena.driver.language import Language
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
        languages = self.metadata.get("languages", None)
        if languages is None:
            return Language.languages()
        return [
            Language.from_name(lang)
            for lang in languages
        ]

    @property
    def public(self):
        return self.metadata.get("public", False)

    @property
    def title(self):
        return self.metadata.get("title", self.name)

    def problem(self, name):
        path = os.path.join(self.directory, name)
        if not os.path.isdir(path):
            return None
        return Problem(self, name)

    def to_json(self):
        return json.dumps({
            "name": self.name,
            "title": self.title,
            "public": self.public,
            "languages": [l.name for l in self.languages],
            "problems": [p.name for p in self.problems]
        })
