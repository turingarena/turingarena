import logging
import os
import subprocess
from collections import namedtuple
from contextlib import contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


class GitManager(namedtuple("GitManager", ["git_dir"])):
    @property
    @lru_cache(None)
    def _base_env(self):
        return {
            "GIT_DIR": self.git_dir,
            "GIT_AUTHOR_NAME": "TuringArena",
            "GIT_AUTHOR_EMAIL": "contact@turingarena.org",
            "GIT_COMMITTER_NAME": "TuringArena",
            "GIT_COMMITTER_EMAIL": "contact@turingarena.org",
        }

    def git_fetch_repositories(self, repositories):
        for repository in repositories:
            # TODO: add a way to specify branch and depth
            logger.info(f"Fetching git repository {repository}")
            subprocess.call(["git", "fetch", "--recurse-submodules=yes", repository], env=self._base_env)

    @contextmanager
    def _temp_index(self):
        with TemporaryDirectory() as temp_dir:
            yield {
                **self._base_env,
                "GIT_INDEX_FILE": os.path.join(temp_dir, "index"),
            }

    def git_import_trees(self, tree_ids, dest):
        for tree_id in tree_ids:
            with self._temp_index() as env:
                logger.info(f"Importing git tree id {tree_id}")
                subprocess.call(["git", "read-tree", tree_id], env=env)
                subprocess.call(["git", f"--work-tree={dest}", "checkout-index", "--all"], env=env)

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
