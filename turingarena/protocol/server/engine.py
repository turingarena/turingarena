from collections import deque
from contextlib import contextmanager

from turingarena.protocol.server.commands import ProxyRequest
from turingarena.protocol.server.frames import Frame, StatementContext, Phase, FrameState, logger


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
        logger.debug("ensure_output")
        if not self.input_sent:
            logger.debug("sending input on downward pipe")
            next(self.run_generator)
        self.input_sent = True

    def flush(self):
        assert self.input_sent
        self.input_sent = False

    def push_callback(self, callback):
        self.callback_queue.append(callback)

    def pop_callback(self):
        return self.callback_queue.popleft()