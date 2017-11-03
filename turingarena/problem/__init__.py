import importlib
from abc import abstractmethod

from turingarena.common import TupleLikeObject, ImmutableObject
from turingarena.evaluation import Task, TaskDescription


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
    __slots__ = ["goals", "submission_items"]

    def __init__(self):
        self.goals = {}
        self.submission_items = {}

    def goal(self, checker=None, *, name=None):
        if checker and not name:
            name = checker.__name__

        assert name is not None
        assert name not in self.goals

        goal = Goal(self, name, checker=checker)
        self.goals[name] = goal
        return goal

    def implementation_submission_item(self, name, **kwargs):
        assert name is not None
        assert name not in self.submission_items

        item = ImplementationSubmissionItem(**kwargs)
        self.submission_items[name] = item
        return item


class SubmissionItem(ImmutableObject):
    __slots__ = []

    @abstractmethod
    def dependencies(self):
        pass

    @abstractmethod
    def resolve(self):
        pass


class ImplementationSubmissionItem(SubmissionItem):
    __slots__ = ["protocol_name", "interface_name"]

    def dependencies(self):
        # TODO: compile the submission
        return []

    def resolve(self):
        # FIXME: install the protocol file
        protocol_module = importlib.import_module(
            f"turingarena_protocols.{self.protocol_name}"
        )
        interface_signature = getattr(protocol_module, self.interface_name)


class Goal:
    def __init__(self, problem, name, *, checker):
        self.problem = problem
        self.checker = checker
        self.dependencies = []
        self.name = name

    def evaluate(self):
        submission = {
            name: item.resolve()
            for name, item in self.problem.submission_items.items()
        }
        return self.checker(**submission)

    def to_command(self, problem_id):
        return (
            problem_id.to_command() +
            f" goal"
            f" --name {self.name}"
        )

    def to_task(self, problem_id):
        return Task(self.to_command(problem_id) + " task")

    def to_task_description(self, problem_id):
        return TaskDescription(
            command=self.to_command(problem_id) + " evaluate",
            dependencies=[],
        )
