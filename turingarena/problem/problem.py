import importlib
import importlib.util
import logging
import os
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import yaml

from turingarena.common import ImmutableObject
from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.metadata import TuringarenaYamlLoader
from turingarena.problem.python import HostPythonEvaluator
from turingarena.sandbox.source import AlgorithmSource

logger = logging.getLogger(__name__)


class AlgorithmicProblem(ImmutableObject):
    __slots__ = [
        "interface",
        "extra_metadata",
        "algorithm_sources",
        "evaluator",
    ]

    def compile_algorithms(self, evaluation_dir):
        algorithms_dir = os.path.join(evaluation_dir, "algorithms")
        os.mkdir(algorithms_dir)
        for name, source in self.algorithm_sources.items():
            algorithm_dir = os.path.join(algorithms_dir, name)
            source.compile(algorithm_dir)

    @contextmanager
    def prepare(self):
        with TemporaryDirectory(dir="/tmp", prefix="turingarena_problem_") as prepared_problem_dir:
            self.compile_algorithms(prepared_problem_dir)
            yield prepared_problem_dir

    @contextmanager
    def prepare_submission(self, source):
        with TemporaryDirectory(dir="/tmp", prefix="turingarena_submission_") as temp_dir:
            submission_dir = os.path.join(temp_dir, "algorithm")
            source.compile(submission_dir)
            yield submission_dir

    @property
    def metadata(self):
        return {
            **self.extra_metadata,
            **dict(
                interface=self.interface.metadata,
            ),
        }

    def evaluate(self, source):
        with self.prepare() as prepared_problem_dir:
            with self.prepare_submission(source) as submission_dir:
                return self.evaluator.evaluate(
                    prepared_problem_dir=prepared_problem_dir,
                    submission_dir=submission_dir,
                )


def make_problem(dirname):
    with open(os.path.join(dirname, "interface.txt")) as f:
        interface_text = f.read()

    try:
        with open(os.path.join(dirname, "metadata.yaml")) as f:
            extra_metadata = yaml.load(f, Loader=TuringarenaYamlLoader)
    except FileNotFoundError:
        extra_metadata = dict()

    interface = InterfaceDefinition.compile(
        interface_text,
        extra_metadata=extra_metadata.get("interface"),
    )
    return AlgorithmicProblem(
        interface=interface,
        extra_metadata=extra_metadata,
        algorithm_sources=dict(find_algorithm_sources(os.path.join(dirname, "algorithms"), interface=interface)),
        evaluator=HostPythonEvaluator(script_path=os.path.join(dirname, "evaluate.py"))
    )


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


def load_problem(problem_name):
    problem_package = importlib.import_module(problem_name)
    try:
        paths = problem_package.__path__
    except AttributeError:
        raise ValueError(f"problem module {problem_package} is not a package")
    assert len(paths) >= 1
    if len(paths) > 1:
        raise ValueError(f"problem package {problem_package} has multiple paths: {paths}")
    [path] = paths
    return make_problem(path)


LANGUAGE_BY_EXTENSION = {
    ".cpp": "c++",
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
}


def find_algorithm_sources(directory, *, interface):
    root, directories, files = next(os.walk(directory))

    for source_filename in files:
        yield source_filename, load_source_file(directory, source_filename, interface=interface)


def load_source_file(directory, source_filename, *, interface):
    base, ext = os.path.splitext(source_filename)
    source_path = os.path.join(directory, source_filename)
    with open(source_path) as f:
        source_text = f.read()
    return AlgorithmSource.load(
        source_text,
        language=LANGUAGE_BY_EXTENSION[ext],
        interface=interface,
    )
