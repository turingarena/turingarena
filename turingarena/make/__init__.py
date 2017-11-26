import logging
import subprocess

import git
import multiprocessing

import os
from collections import OrderedDict
from functools import partial
from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class Task(ImmutableObject):
    __slots__ = ["name", "target", "dependencies"]

    def __init__(self, target, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = target.__name__
        super().__init__(target=target, **kwargs)

    def run(self):
        self.target()

    def compute(self, *, parents, repo_path):
        logger.debug(f"running task '{self}' with parents: {parents} in repo '{repo_path}'")

        root_repo = git.Repo(path=repo_path)

        with TemporaryDirectory() as temp_dir:
            repo = root_repo.clone(path=temp_dir)

            for parent in parents:
                repo.remote("origin").fetch(parent)
                repo.index.merge_tree(repo.commit(parent))

            repo.index.checkout()

            def target():
                os.chdir(repo.working_dir)
                self.run()

            process = multiprocessing.Process(
                target=target,
            )
            process.start()
            process.join()
            if process.exitcode:
                raise RuntimeError(f"task failed (error code {process.exitcode})")

            repo.index.add("*")

            commit = repo.index.commit(
                f"turingarena compute '{self.name}'",
                parent_commits=[
                    repo.commit(parent)
                    for parent in parents
                ],
            )

            repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")
            logger.debug(f"commit message: {commit.message}")

            return commit

    def get_tasks(self):
        return [self]


def resolve_plan(tasks):
    cache = OrderedDict()

    def dfs(node):
        try:
            cached = cache[node.name]
            assert cached == node
            return
        except KeyError:
            pass

        for d in node.dependencies:
            dfs(d)
        cache[node.name] = node

    for t in tasks:
        dfs(t)
    return cache


def task(*deps, **kwargs):
    return partial(Task, **kwargs, dependencies=list(deps))

