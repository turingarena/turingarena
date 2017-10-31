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


class InterfaceEnvironment:
    __slots__ = [
        "interface",
        "root_frame",
        "frame_cache",
        "callback_queue",
    ]

    def __init__(self, *, interface):
        self.interface = interface
        self.frame_cache = {}
        self.callback_queue = deque()
        self.root_frame = Frame(parent=None, scope_variables=interface.body.scope.variables)

    @contextmanager
    def new_frame(self, *, parent, scope):
        if scope not in self.frame_cache:
            logger.debug(f"creating new frame for scope {scope}")
            self.frame_cache[scope] = Frame(parent=parent, scope_variables=scope.variables)
        frame = self.frame_cache[scope]
        logger.debug(f"entering frame {frame} for scope {scope}")
        yield frame
        logger.debug(f"exiting frame {frame} for scope {scope}")


class PreflightContext:
    __slots__ = [
        "environment",
        "proxy_connection",
        "next_request",
        "input_sent",
        "on_advance",
    ]

    def __init__(self, *, environment, proxy_connection, on_advance):
        self.environment = environment
        self.proxy_connection = proxy_connection
        self.next_request = None
        self.input_sent = False
        self.on_advance = on_advance

    def peek_request(self):
        if self.next_request is None:
            self.next_request = ProxyRequest.accept(
                interface_signature=self.environment.interface.signature,
                file=self.proxy_connection.request_pipe,
            )
        return self.next_request

    def complete_request(self):
        assert self.next_request is not None
        self.next_request = None

    def send_response(self, response):
        response.send(file=self.proxy_connection.response_pipe)

    def advance(self):
        if not self.input_sent:
            self.on_advance()
        self.input_sent = True

    def on_flush(self):
        assert self.input_sent
        self.input_sent = False

    def new_frame(self, *, parent, scope):
        return self.environment.new_frame(parent=parent, scope=scope)

    def pop_callback(self):
        return self.environment.callback_queue.popleft()


class RunContext:
    __slots__ = [
        "process_connection",
        "environment",
    ]

    def __init__(self, *, environment, process_connection):
        self.environment = environment
        self.process_connection = process_connection

    def new_frame(self, *, parent, scope):
        return self.environment.new_frame(parent=parent, scope=scope)

    def push_callback(self, callback):
        self.environment.callback_queue.append(callback)
