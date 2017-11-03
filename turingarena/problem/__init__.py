from turingarena.common import TupleLikeObject
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
    __slots__ = ["goals"]

    def __init__(self):
        self.goals = {}

    def goal(self, checker=None, *, name=None):
        if checker and not name:
            name = checker.__name__

        assert name is not None
        assert name not in self.goals

        goal = Goal(name)
        self.goals[name] = goal
        return goal


class Goal:
    def __init__(self, name):
        self.checker = None
        self.dependencies = []
        self.name = name

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
