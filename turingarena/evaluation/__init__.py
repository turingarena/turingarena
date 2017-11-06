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
            "command": self.command,
            "dependencies": [
                d
                for d in self.dependencies
            ],
            "entries": self.entries,
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


def make_entry(name, file_map):
    with TemporaryDirectory() as temp_dir:
        repo = git.Repo.init(path=temp_dir)

        for source, dest in file_map.items():
            os.makedirs(os.path.join(temp_dir, os.path.dirname(dest)), exist_ok=True)
            shutil.copy(source, os.path.join(temp_dir, dest))

        repo.active_branch.checkout(orphan=f"entry/{name}")
        repo.index.add(".")

        repo.create_head("HEAD")
        commit = repo.commit()
        print(commit.hexsha)
