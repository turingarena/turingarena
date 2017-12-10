import logging
from contextlib import contextmanager
from enum import Enum

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class Phase(Enum):
    PREFLIGHT = 1
    RUN = 2


class FrameState(Enum):
    PRISTINE = 1
    OPEN = 2
    CLOSED = 3


class Frame:
    def __init__(self, *, scope, parent):
        self.scope = scope
        self.parent = parent
        self.values = {
            l: None for l in self.scope.variables.locals().values()
        }
        self.state = {phase: FrameState.PRISTINE for phase in Phase}

    def __getitem__(self, variable):
        if variable in self.values:
            return self.values[variable]
        elif self.parent:
            return self.parent[variable]
        else:
            raise KeyError

    def __setitem__(self, variable, value):
        if variable in self.values:
            self.values[variable] = value
        elif self.parent:
            self.parent[variable] = value
        else:
            raise KeyError

    def __str__(self):
        return str({
            variable.name: value
            for variable, value in self.values.items()
        })

    @contextmanager
    def contextmanager(self, phase):
        assert self.state[phase] is FrameState.PRISTINE
        self.state[phase] = FrameState.OPEN
        yield
        self.state[phase] = FrameState.CLOSED


class StatementContext(ImmutableObject):
    __slots__ = ["engine", "frame", "phase"]

    def evaluate(self, expression):
        return expression.evaluate(frame=self.frame)

    @contextmanager
    def enter(self, scope):
        with self.engine.new_frame(
                parent=self.frame,
                scope=scope,
                phase=self.phase,
        ) as new_frame:
            yield StatementContext(
                engine=self.engine,
                frame=new_frame,
                phase=self.phase,
            )
