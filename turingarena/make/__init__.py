import logging
import multiprocessing

import git
import os
from collections import OrderedDict
from functools import partial
from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class EvaluationNode(ImmutableObject):
    __slots__ = ["name"]


class EvaluationEntry(EvaluationNode):
    __slots__ = []


class Task(EvaluationNode):
    __slots__ = ["dependencies", "target"]

    def __init__(self, target, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = target.__name__
        super().__init__(target=target, **kwargs)

    def run(self):
        self.target()

    def compute(self, *, parents, repo_path):
        logger.debug(f"running task '{self}' with parents: {parents} in repo '{repo_path}'")

        assert set(parents.keys()) == set(d.name for d in self.dependencies)

        root_repo = git.Repo(path=repo_path)

        with TemporaryDirectory() as temp_dir:
            repo = root_repo.clone(path=temp_dir)

            for parent in parents.values():
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
                    for parent in parents.values()
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

        assert isinstance(node, EvaluationNode)
        if isinstance(node, Task):
            for d in node.dependencies:
                dfs(d)

        cache[node.name] = node

    for t in tasks:
        dfs(t)
    return cache


def make_plan_signature(plan):
    return {
        "tasks": [
            {
                "name": task.name,
                "dependencies": [d.name for d in task.dependencies],
            }
            for task in plan.values()
        ]
    }


def task(*deps, **kwargs):
    return partial(Task, **kwargs, dependencies=list(deps))
