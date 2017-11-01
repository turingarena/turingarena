import logging
from collections import deque
from contextlib import contextmanager
from enum import Enum

from turingarena.protocol.model.node import ImmutableObject
from turingarena.protocol.server.commands import ProxyRequest

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


class InterfaceEngine:
    def __init__(self, *, interface, proxy_connection, process_connection):
        self.interface = interface
        self.proxy_connection = proxy_connection
        self.process_connection = process_connection

        self.root_frame = Frame(parent=None, scope=interface.body.scope)
        self.frame_cache = {}
        self.callback_queue = deque()
        self.next_request = None
        self.input_sent = False

        self.run_generator = self.interface.run(StatementContext(
            engine=self,
            frame=self.root_frame,
            phase=Phase.RUN,
        ))

    def run(self):
        next(self.interface.run(StatementContext(
            engine=self,
            frame=self.root_frame,
            phase=Phase.PREFLIGHT,
        )))

    @contextmanager
    def new_frame(self, *, parent, scope, phase):
        try:
            frame = self.frame_cache[scope]
        except KeyError:
            frame = None

        if frame:
            if frame.state[phase] is FrameState.CLOSED:
                logger.debug(f"not reusing frame {frame}")
                del self.frame_cache[scope]
                frame = None
            else:
                logger.debug(f"reusing frame {frame}")

        if not frame:
            frame = self.frame_cache[scope] = Frame(
                parent=parent,
                scope=scope,
            )
            logger.debug(f"created new frame {frame} for scope {scope} ({phase})")

        with frame.contextmanager(phase=phase):
            yield frame

    def peek_request(self):
        if self.next_request is None:
            self.next_request = ProxyRequest.accept(
                map(str.strip, self.proxy_connection.request_pipe),
                interface_signature=self.interface.signature,
            )
        return self.next_request

    def complete_request(self):
        assert self.next_request is not None
        self.next_request = None

    def send_response(self, response):
        file = self.proxy_connection.response_pipe
        for line in response.serialize():
            print(line, file=file)
        file.flush()

    def ensure_output(self):
        if not self.input_sent:
            next(self.run_generator)
        self.input_sent = True

    def flush(self):
        assert self.input_sent
        self.input_sent = False

    def push_callback(self, callback):
        self.callback_queue.append(callback)

    def pop_callback(self):
        return self.callback_queue.popleft()


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
