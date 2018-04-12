import logging
import os
import subprocess
from collections import namedtuple
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import yaml

from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.metadata import TuringarenaYamlLoader
from turingarena.loader import find_package_path, split_module
from turingarena.problem.python import HostPythonEvaluator

logger = logging.getLogger(__name__)


class AlgorithmicProblem(namedtuple("AlgorithmicProblem", [
    "interface",
    "evaluator",
])):
    __slots__ = []

    @property
    def metadata(self):
        return {
            **self.extra_metadata,
            **dict(
                interface=self.interface.metadata,
            ),
        }

    def evaluate(self, source):
        # FIXME: we should expect source_name, language_name
        with TemporaryDirectory() as temp_dir:
            source_path = os.path.join(temp_dir, "source.txt")
            with open(source_path, "w") as f:
                f.write(source.text)
            return self.evaluator.evaluate(
                source_name=f":{source_path}",
                language_name=source.language.name,
            )


def load_problem(problem_name=None):
    mod, _ = split_module(problem_name)
    interface_name = problem_name
    return AlgorithmicProblem(
        interface=InterfaceDefinition.load(interface_name),
        evaluator=HostPythonEvaluator(mod, interface_name=interface_name),
    )


def load_problem_metadata(name):
    mod, rel_path = split_module(name, default_arg="metadata.yaml")
    try:
        with open(find_package_path(mod, rel_path)) as f:
            return yaml.load(f, Loader=TuringarenaYamlLoader)
    except FileNotFoundError:
        return dict()


@contextmanager
def clone_from_git(url):
    with TemporaryDirectory(dir="/tmp", prefix="turingarena_git") as git_dir:
        logger.info(f"cloning problem {url} from git into directory {git_dir}")
        cmd = [
            "git",
            "clone",
            "--depth=1",
            "--recurse-submodules",
            "--shallow-submodules",
            "--jobs=8",
            "--quiet",
            url,
            ".",
        ]
        logger.info(f"running {cmd}")
        subprocess.run(cmd, cwd=git_dir, check=True)

        import sys
        sys.path.append(git_dir)
        yield
        sys.path.remove(git_dir)
