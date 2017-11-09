from abc import abstractmethod

from turingarena.common import TupleLikeObject, ImmutableObject
from turingarena.make import TaskDescription
from turingarena.protocol.proxy.python.client import Implementation


class ProblemIdentifier(TupleLikeObject):
    __slots__ = ["module", "name"]

    def load(self):
        module = __import__(self.module)
        return getattr(module, self.name)

    def to_command(self):
        return (
            f"turingarena problem"
            f" --module {self.module}"
            f" --name {self.name}"
        )


class Problem:
    __slots__ = ["goals", "entries"]

    def __init__(self):
        self.goals = {}
        self.entries = {}

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
    def dependencies(self, *, problem_id):
        pass

    @abstractmethod
    def resolve(self):
        pass


class ImplementationEntry(Entry):
    __slots__ = ["protocol_id", "interface_name"]

    def dependencies(self, *, problem_id):
        return [
            f"{problem_id.to_command()}"
            f" entry --name {self.name}"
            f" compile task"
            ,
        ]

    def compile_task_description(self):
        return TaskDescription(
            command=(
                f"turingarena sandbox compile"
                f" --protocol {self.protocol_id.name()}"
                f" --interface {self.interface_name}"
                f" -o {self.name}"
                f" {self.name}.cpp"
            ),
            entries=[f"{self.name}"],
        )

    def algorithm_name(self):
        return self.name

    def resolve(self):
        return Implementation(
            protocol_id=self.protocol_id,
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

    def to_command(self, problem_id):
        return (
            problem_id.to_command() +
            f" goal"
            f" --name {self.name}"
        )

    def to_task(self, problem_id):
        return self.to_command(problem_id) + " task"

    def to_task_description(self, problem_id):
        return TaskDescription(
            command=self.to_command(problem_id) + " evaluate",
            dependencies=[
                d
                for entry in self.problem.entries.values()
                for d in entry.dependencies(problem_id=problem_id)
            ],
        )
