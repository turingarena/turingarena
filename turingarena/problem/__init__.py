import os
from abc import abstractmethod

from turingarena.common import ImmutableObject
from turingarena.make import Task, EvaluationEntry
from turingarena.protocol.client import ProxiedAlgorithm
from turingarena.sandbox.algorithm import Algorithm
from turingarena.sandbox.loader import load_algorithm_source, load_algorithm_executable


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
    def get_nodes(self):
        pass

    @abstractmethod
    def resolve(self):
        pass


class ImplementationEntry(Entry):
    __slots__ = ["protocol_name", "interface_name"]

    def get_nodes(self):
        yield Task(
            name=f"compile_{self.name}",
            target=self.target,
            dependencies=[
                EvaluationEntry(name=f"entry_{self.name}")
            ],
        )

    def target(self):
        source = self.load_source()
        os.makedirs("algorithms", exist_ok=True)
        source.compile(algorithm_dir=self.algorithm_dir)

    @property
    def algorithm_dir(self):
        return os.path.join("algorithms", self.name)

    def load_source(self):
        return load_algorithm_source(
            filename=f"{self.name}.cpp",
            protocol_name=self.protocol_name,
            interface_name=self.interface_name,
        )

    def load_executable(self):
        return load_algorithm_executable(algorithm_dir=self.algorithm_dir)

    def algorithm_name(self):
        return self.name

    def resolve(self):
        return ProxiedAlgorithm(
            algorithm=Algorithm(
                source=self.load_source(),
                executable=self.load_executable(),
            ),
        )


class Goal:
    def __init__(self, problem, name, *, checker):
        self.problem = problem
        self.checker = checker
        self.dependencies = []
        self.name = name

    def goal_dir(self):
        return os.path.join("goals", self.name)

    def evaluate(self):
        submission = {
            name: item.resolve()
            for name, item in self.problem.entries.items()
        }
        result = self.checker(**submission)

        os.makedirs(self.goal_dir(), exist_ok=True)
        with open(os.path.join(self.goal_dir(), "result.txt"), "w") as result_file:
            print(result, file=result_file)

    def main_task(self):
        return Task(
            target=self.evaluate,
            name=f"evaluate_{self.name}",
            dependencies=[
                t
                for entry in self.problem.entries.values()
                for t in entry.get_nodes()
            ],
        )
