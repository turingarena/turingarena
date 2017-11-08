import json
import logging
import subprocess

import git
import os
import shutil
from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject, TupleLikeObject

logger = logging.getLogger(__name__)


def load_task_description(task):
    with TemporaryDirectory() as dir:
        result = subprocess.run(
            task,
            cwd=dir,
            shell=True,
            stdout=subprocess.PIPE,
        )
    return TaskDescription(**json.loads(result.stdout))


class TaskDescription(ImmutableObject):
    __slots__ = ["command", "dependencies", "entries"]

    def __init__(self, command, *, dependencies=None, entries=None):
        super().__init__(
            command=command,
            dependencies=dependencies or [],
            entries=entries or [],
        )

    def to_json(self):
        return json.dumps({
            slot: getattr(self, slot)
            for slot in self.all_slots()
        }, indent=4)


class EvaluationPlan(ImmutableObject):
    __slots__ = ["root_task", "description_cache", "entries"]

    def __init__(self, root_task):
        super().__init__(
            description_cache={},
            entries=set(),
            root_task=root_task,
        )

        self.resolve()

    def resolve(self):
        logger.debug(f"building plan for task '{self.root_task}'")
        stack = [self.root_task]

        while stack:
            top_task = stack.pop()
            logger.debug(f"popped task '{top_task}'")
            if top_task in self.description_cache:
                logger.debug(f"cache hit")
                continue

            description = load_task_description(top_task)
            self.description_cache[top_task] = description

            for entry in description.entries:
                logger.debug(f"adding entry {entry}")
                self.entries.add(entry)

            for dep in description.dependencies:
                logger.debug(f"pushing dependency '{dep}'")
                assert dep not in stack
                stack.append(dep)


def evaluate_task(root_task):
    plan = EvaluationPlan(root_task)
    done = {
        task: False
        for task in plan.description_cache
    }

    with TemporaryDirectory() as eval_dir:
        def dfs(task):
            if done[task]:
                return

            description = plan.description_cache[task]

            for d in description.dependencies:
                dfs(d)

            subprocess.run(
                description.command,
                shell=True,
                cwd=eval_dir,
            )
            done[task] = True
        dfs(root_task)


def compute_task(task, *, repo_path, deps, entries):
    description = load_task_description(task)
    assert len(description.dependencies) == len(deps)
    assert len(description.entries) == len(entries)

    root_repo = git.Repo(path=repo_path)

    with TemporaryDirectory() as temp_dir:
        repo = root_repo.clone(path=temp_dir)

        for dep in entries + deps:
            repo.remote("origin").fetch(f"sha-{dep}")
            repo.index.merge_tree(repo.commit(dep))

        repo.index.checkout()

        subprocess.run(
            description.command,
            shell=True,
            cwd=repo.working_dir,
        )

        repo.index.add("*")

        commit = repo.index.commit(f"turingarena compute '{task}'")

        repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")
        logger.debug(f"commit message: {commit.message}")
        print(commit.hexsha)


def make_entry(name, *, file_map, repo_path):
    root_repo = git.Repo(path=repo_path)

    with TemporaryDirectory() as temp_dir:
        repo = root_repo.clone(path=temp_dir)

        for source, dest in file_map.items():
            os.makedirs(os.path.join(temp_dir, os.path.dirname(dest)), exist_ok=True)
            shutil.copy(source, os.path.join(temp_dir, dest))

        repo.index.add("*")
        commit = repo.index.commit(f"turingarena entry {name}")
        repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")

        logger.debug(f"commit message: {commit.message}")

        print(commit.hexsha)
