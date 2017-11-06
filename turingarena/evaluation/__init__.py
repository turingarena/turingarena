import json
import logging
import subprocess

from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject, TupleLikeObject

logger = logging.getLogger(__name__)


class Task(TupleLikeObject):
    __slots__ = ["meta_command"]

    def __init__(self, meta_command):
        super().__init__(meta_command=meta_command)

    def resolve(self):
        with TemporaryDirectory() as dir:
            result = subprocess.run(
                self.meta_command,
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
                d.meta_command
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

            description = top_task.resolve()
            self.description_cache[top_task] = description

            for entry in description.entries:
                logger.debug(f"adding entry {entry}")
                self.entries.add(entry)

            for dep_cmd in description.dependencies:
                dep = Task(dep_cmd)
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
                dfs(Task(d))

            subprocess.run(
                description.command,
                shell=True,
                cwd=eval_dir,
            )
            done[task] = True
        dfs(root_task)
