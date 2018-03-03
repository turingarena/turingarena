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
    def open(self, phase):
        assert self.state[phase] is FrameState.PRISTINE
        self.state[phase] = FrameState.OPEN
        yield
        self.state[phase] = FrameState.CLOSED


class ActivationRecord(ImmutableObject):
    __slots__ = ["callback", "frame_cache"]

    def __init__(self, callback=None):
        super().__init__(
            callback=callback,
            frame_cache={},
        )

    @contextmanager
    def new_frame(self, *, parent, scope, phase):
        frame = self._lookup_frame_cache(phase, scope)

        if not frame:
            frame = self.frame_cache[scope] = Frame(
                parent=parent,
                scope=scope,
            )

        with frame.open(phase=phase):
            yield frame

    def _lookup_frame_cache(self, phase, scope):
        try:
            frame = self.frame_cache[scope]
        except KeyError:
            return None

        if frame.state[phase] is FrameState.CLOSED:
            del self.frame_cache[scope]
            return None

        return frame


class StatementContext(ImmutableObject):
    __slots__ = ["engine", "activation_record", "frame", "phase"]

    def evaluate(self, expression):
        return expression.evaluate(frame=self.frame)

    @contextmanager
    def enter(self, scope):
        with self.activation_record.new_frame(
                parent=self.frame,
                scope=scope,
                phase=self.phase,
        ) as new_frame:
            yield StatementContext(
                engine=self.engine,
                activation_record=self.activation_record,
                frame=new_frame,
                phase=self.phase,
            )
