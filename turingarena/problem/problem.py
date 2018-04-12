import importlib
import importlib.util
import logging
import os
import subprocess
import types
from collections import namedtuple
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import yaml
from future.moves import sys

from turingarena.interface.interface import InterfaceDefinition
from turingarena.interface.metadata import TuringarenaYamlLoader
from turingarena.problem.python import HostPythonEvaluator
from turingarena.sandbox.languages.language import Language, UnknownFileExtension

logger = logging.getLogger(__name__)

root_module_name = "__turingarena_root__"
root_problem_module = types.ModuleType(root_module_name)
root_problem_module.__package__ = root_problem_module.__name__
root_problem_module.__path__ = sys.path
sys.modules[root_module_name] = root_problem_module


class AlgorithmicProblem(namedtuple("AlgorithmicProblem", [
    "interface",
    "extra_metadata",
    "algorithm_sources",
    "evaluator",
])):
    __slots__ = []

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


def load_interface(interface_name=None):
    if interface_name is None:
        mod = root_problem_module
    else:
        mod = importlib.import_module(interface_name)
    text = load_interface_text(mod)
    return InterfaceDefinition.compile(text)


def load_interface_text(mod):
    for path in get_problem_paths(mod):
        try:
            with open(os.path.join(path, "interface.txt")) as f:
                return f.read()
        except FileNotFoundError:
            pass
    raise ValueError("no interface file found")


def load_problem_metadata(mod):
    for path in get_problem_paths(mod):
        try:
            with open(os.path.join(path, "metadata.yaml")) as f:
                return yaml.load(f, Loader=TuringarenaYamlLoader)
        except FileNotFoundError:
            pass
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


def load_problem(problem_name=None):
    if problem_name is None:
        mod = root_problem_module
    else:
        mod = importlib.import_module(problem_name)
    interface = load_interface(problem_name)
    return AlgorithmicProblem(
        interface=interface,
        extra_metadata=dict(),  # FIXME
        algorithm_sources=dict(find_algorithm_sources(mod, interface=interface)),
        evaluator=HostPythonEvaluator(mod),
    )


def get_problem_paths(problem_module):
    try:
        return problem_module.__path__
    except AttributeError:
        raise ValueError(f"problem module {problem_module} is not a package")


def find_algorithm_sources(mod, *, interface, directory_name="solutions"):
    for path in get_problem_paths(mod):
        for root, directories, files in os.walk(os.path.join(path, directory_name)):
            for source_filename in files:
                source_path = os.path.join(root, source_filename)
                try:
                    yield source_filename, load_source_file(
                        source_path,
                        interface=interface,
                    )
                except UnknownFileExtension:
                    logger.warning(f"skipping file with unknown extension: {source_path}")


def load_source_file(source_path, *, interface):
    directory, source_filename = os.path.split(source_path)
    base, ext = os.path.splitext(source_filename)
    language = Language.from_extension(ext)
    with open(source_path) as f:
        source_text = f.read()
    return language.source(
        interface=interface,
        language=language,
        text=source_text,
    )
