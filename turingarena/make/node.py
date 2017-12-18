import importlib
import logging
import multiprocessing
import os
from collections import OrderedDict
from functools import partial
from tempfile import TemporaryDirectory

import git

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class EvaluationNode(ImmutableObject):
    __slots__ = ["name", "target"]

    def __init__(self, target=None, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = f"{target.__module__}:{target.__qualname__}"
        super().__init__(target=target, **kwargs)


class EvaluationEntry(EvaluationNode):
    __slots__ = []


class Task(EvaluationNode):
    __slots__ = ["dependencies"]

    def run(self):
        self.target()

    def compute(self, *, parents, repo_path):
        logger.debug(f"running task '{self}' with parents: {parents} in repo '{repo_path}'")

        assert set(parents.keys()) == set(d.name for d in self.dependencies)
        assert all(isinstance(p, str) for p in parents.values())

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


def load_anchor(name):
    module_name, qualname = name.split(":", 2)
    anchor_module = importlib.import_module(module_name)
    return getattr(anchor_module, qualname)


def load_plan(name):
    anchor = load_anchor(name)
    return resolve_plan(anchor.get_tasks())


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
                "name": node.name,
                "dependencies": [d.name for d in node.dependencies],
            }
            for node in plan.values()
            if isinstance(node, Task)
        ],
        "entries": [
            {
                "name": node.name,
            }
            for node in plan.values()
            if isinstance(node, EvaluationEntry)
        ]
    }


def task(*deps, **kwargs):
    return partial(Task, **kwargs, dependencies=list(deps))


def entry(**kwargs):
    return partial(EvaluationEntry, **kwargs)
