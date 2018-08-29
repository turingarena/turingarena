import logging
import os
import subprocess
from collections import namedtuple
from contextlib import contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena_common.git_common import GIT_BASE_ENV

logger = logging.getLogger(__name__)


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
            "git", "init", "--bare"
        ], env=self._base_env, check=True)

    def fetch_repository(self, repository):
        logger.info(f"Fetching git repository {repository}")

        assert repository["type"] == "git_clone"
        url = repository["url"]
        branch = repository["branch"]
        depth = repository["depth"]

        if depth is not None:
            depth_options = [f"--depth={depth}"]
        else:
            depth_options = []

        if branch is not None:
            branch_options = [branch]
        else:
            branch_options = []

        cmd = [
            "git",
            "fetch",
            "--recurse-submodules=yes",
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

    def checkout_trees(self, ids, dest):
        for id in ids:
            with self._temp_index() as env:
                subprocess.run([
                    "git",
                    "read-tree",
                    id,
                ], env=env, check=True)
                subprocess.run([
                    "git",
                    f"--work-tree={dest}",
                    "checkout-index",
                    "--all",
                ], env=env, check=True)

    def add_directory(self, directory):
        logger.info(f"Add directory {directory} to be committed")
        subprocess.call(["git", "add", "-A", directory], env=self._base_env)

    def commit_work(self, src):
        logger.info("Committing work")

        with self._temp_index() as env:
            tree_id = subprocess.check_output([
                "git", f"--work-tree={src}", "write-tree"
            ], env=env).strip().decode("ascii")
            logger.info(f"Output written with tree-id {tree_id}")

            commit_id = subprocess.check_output([
                "git", "commit-tree", tree_id, "-m", "Make output"
            ], env=env).strip().decode("ascii")
            logger.info(f"Created commit with commit-id {commit_id}")

            return tree_id, commit_id
