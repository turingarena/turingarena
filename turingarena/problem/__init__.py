from abc import abstractmethod
from functools import partial

from turingarena.common import ImmutableObject
from turingarena.make import Task
from turingarena.protocol.proxy.python.engine import Implementation
from turingarena.sandbox.compile import sandbox_compile


class Problem:
    __slots__ = ["goals", "entries"]

    def __init__(self):
        self.goals = {}
        self.entries = {}

    def get_tasks(self):
        for goal in self.goals.values():
            yield goal.main_task()

    def goal(self, checker=None, *, name=None):
        if checker and not name:
            name = checker.__name__

        assert name is not None
        assert name not in self.goals

        goal = Goal(self, name, checker=checker)
        self.goals[name] = goal
        return goal

    def implementation_entry(self, name, **kwargs):
        assert name is not None
        assert name not in self.entries

        entry = ImplementationEntry(problem=self, name=name, **kwargs)
        self.entries[name] = entry
        return entry


class Entry(ImmutableObject):
    __slots__ = ["problem", "name"]

    @abstractmethod
    def get_tasks(self):
        pass

    @abstractmethod
    def resolve(self):
        pass


class ImplementationEntry(Entry):
    __slots__ = ["protocol_name", "interface_name"]

    def get_tasks(self):
        yield Task(
            name=f"compile_{self.name}",
            target=partial(
                sandbox_compile,
                protocol_name=self.protocol_name,
                interface_name=self.interface_name,
                algorithm_name=self.name,
                source_filename=f"{self.name}.cpp",
            ),
            dependencies=[],
        )

    def algorithm_name(self):
        return self.name

    def resolve(self):
        return Implementation(
            protocol_name=self.protocol_name,
            interface_name=self.interface_name,
            algorithm_name=self.algorithm_name(),
        )


class Goal:
    def __init__(self, problem, name, *, checker):
        self.problem = problem
        self.checker = checker
        self.dependencies = []
        self.name = name

    def evaluate(self):
        submission = {
            name: item.resolve()
            for name, item in self.problem.entries.items()
        }
        return self.checker(**submission)

    def main_task(self):
        return Task(
            target=self.evaluate,
            name=f"goal_{self.name}",
            dependencies=[
                t
                for entry in self.problem.entries.values()
                for t in entry.get_tasks()
            ],
        )
