import json
import subprocess

from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject, TupleLikeObject


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

        self.resolve_recursively()

    def resolve_recursively(self):
        stack = [self.root_task]

        while stack:
            top_task = stack.pop()
            if top_task in self.description_cache:
                continue

            description = top_task.resolve()
            self.description_cache[top_task] = description

            for entry in description.entries:
                self.entries.add(entry)

            for dep_cmd in description.dependencies:
                dep = Task(dep_cmd)
                assert dep not in stack
                stack.append(dep)
