import logging
from collections import deque
from contextlib import contextmanager

from turingarena.protocol.server.commands import ProxyRequest

logger = logging.getLogger(__name__)


class Frame:
    __slots__ = ["scope_variables", "parent", "values"]

    def __init__(self, *, scope_variables, parent):
        self.scope_variables = scope_variables
        self.parent = parent
        self.values = {
            l: None for l in self.scope_variables.locals().values()
        }

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


class PreflightContext:
    __slots__ = [
        "proxy_connection",
        "interface",
        "frame_cache",
        "next_request",
        "input_sent",
        "on_advance",
        "root_frame",
        "callback_queue",
    ]

    def __init__(self, *, proxy_connection, interface, on_advance):
        self.proxy_connection = proxy_connection
        self.interface = interface
        self.frame_cache = {}
        self.next_request = None
        self.input_sent = False
        self.on_advance = on_advance
        self.callback_queue = deque()
        self.root_frame = Frame(parent=None, scope_variables=interface.body.scope.variables)

    def peek_request(self):
        if self.next_request is None:
            self.next_request = ProxyRequest.accept(
                interface_signature=self.interface.signature,
                file=self.proxy_connection.request_pipe,
            )
        return self.next_request

    def complete_request(self):
        assert self.next_request is not None
        self.next_request = None

    @contextmanager
    def new_frame(self, *, parent, scope):
        logger.debug(f"entering preflight frame for scope {scope}")
        assert scope not in self.frame_cache
        frame = Frame(parent=parent, scope_variables=scope.variables)
        self.frame_cache[scope] = frame
        yield frame
        logger.debug(f"exiting preflight frame {frame} for scope {scope} (frame cache: {self.frame_cache})")

    def advance(self):
        if not self.input_sent:
            self.on_advance()
        self.input_sent = True

    def on_flush(self):
        assert self.input_sent
        self.input_sent = False

    def pop_callback(self):
        return self.callback_queue.popleft()


class RunContext:
    __slots__ = [
        "process_connection",
        "interface",
        "frame_cache",
        "active_frames",
        "callback_queue",
        "root_frame"
    ]

    def __init__(self, *, process_connection, interface, preflight_context, callback_queue, root_frame):
        self.process_connection = process_connection
        self.interface = interface
        self.frame_cache = preflight_context.frame_cache
        self.active_frames = set()
        self.callback_queue = callback_queue
        self.root_frame = root_frame

    @contextmanager
    def new_frame(self, *, parent, scope):
        if parent:
            assert scope not in self.active_frames
            self.active_frames.add(scope)
        if scope not in self.frame_cache:
            self.frame_cache[scope] = Frame(
                parent=parent,
                scope_variables=scope.variables,
            )
        frame = self.frame_cache[scope]
        logger.debug(f"entering run frame {frame} for scope {scope}")
        yield frame
        logger.debug(f"exiting run frame {frame} for scope {scope} (frame cache: {self.frame_cache})")
        if parent:
            self.active_frames.remove(scope)
        del self.frame_cache[scope]

    def push_callback(self, callback):
        self.callback_queue.append(callback)
