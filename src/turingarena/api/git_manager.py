import logging
import os
import re
import subprocess
from collections import namedtuple
from contextlib import contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena_common.commands import GitRepository, WorkingDirectory
from turingarena_common.git_common import GIT_BASE_ENV

logger = logging.getLogger(__name__)

GITHUB_REPO_PATTERN = re.compile("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class GitManager(namedtuple("GitManager", ["git_dir"])):
    @property
    @lru_cache(None)
    def _base_env(self):
        return {
            "GIT_DIR": self.git_dir,
            **GIT_BASE_ENV,
        }

    def init(self):
        subprocess.run([
            "git", "init", "--bare", "--quiet"
        ], env=self._base_env, check=True)

    def fetch_repository(self, repository: GitRepository):
        logger.info(f"Fetching git repository {repository}")

        if GITHUB_REPO_PATTERN.match(repository.url):
            url = f"https://github.com/{repository.url}"
        else:
            url = repository.url

        if repository.depth is not None:
            depth_options = [f"--depth={repository.depth}"]
        else:
            depth_options = []

        if repository.branch is not None:
            branch_options = [repository.branch]
        else:
            branch_options = []

        cmd = [
            "git",
            "fetch",
            "--recurse-submodules=yes",
            "--quiet",
            *depth_options,
            url,
            *branch_options,
        ]
        logging.debug(f"running {cmd}")
        subprocess.run(cmd, env=self._base_env, check=True)

    @contextmanager
    def _temp_index(self):
        with TemporaryDirectory() as temp_dir:
            yield {
                **self._base_env,
                "GIT_INDEX_FILE": os.path.join(temp_dir, "index"),
            }

    def checkout_commit(self, oid, dest):
        with self._temp_index() as env:
            subprocess.run([
                "git",
                "read-tree",
                oid,
            ], env=env, check=True)
            subprocess.run([
                "git",
                f"--work-tree={dest}",
                "checkout-index",
                "--all",
            ], env=env, check=True)


@contextmanager
def create_working_directory(working_directory: WorkingDirectory):
    git = GitManager("/run/turingarena/db.git")
    git.init()

    with TemporaryDirectory() as temp_dir:
        logging.info(f"Unpacking working directory in {temp_dir}")

        if working_directory.pack.repository is not None:
            git.fetch_repository(working_directory.pack.repository)
        git.checkout_commit(working_directory.pack.oid, temp_dir)

        yield temp_dir
