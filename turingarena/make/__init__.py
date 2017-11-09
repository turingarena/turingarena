import json
import logging
import subprocess

from tempfile import TemporaryDirectory

from turingarena.common import ImmutableObject

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


def subprocess_compute(task_command, *, compute_command, parents):
    dep_options = " ".join(
        f"--parent {parent}"
        for parent in parents
    )

    combined_command = f"{compute_command} {dep_options} {task_command}"

    logger.debug(f"executing '{combined_command}'")
    process = subprocess.run(
        combined_command,
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        check=True,
    )
    return process.stdout.strip()


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


class SequentialMaker:
    def __init__(self, target, *, compute, entries):
        self.target = target
        self.compute = compute
        self.plan = EvaluationPlan(target)
        self.entries = entries

        self.results = None

    def run(self):
        self.results = {
            task: None
            for task in self.plan.description_cache
        }
        try:
            return self.dfs(self.target)
        finally:
            self.results = None

    def dfs(self, task):
        if self.results[task]:
            return
        description = self.plan.description_cache[task]

        for d in description.dependencies:
            self.dfs(d)

        self.results[task] = self.compute(
            description.command,
            parents=[
                self.results[dep]
                for dep in description.dependencies
            ] + [
                self.entries[entry]
                for entry in description.entries
            ],
        )
