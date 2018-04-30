import logging
import subprocess
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import yaml

from turingarena_impl.interface.metadata import TuringarenaYamlLoader
from turingarena_impl.loader import find_package_path

logger = logging.getLogger(__name__)


def load_problem_metadata(name):
    try:
        with open(find_package_path(name, "metadata.yaml")) as f:
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
