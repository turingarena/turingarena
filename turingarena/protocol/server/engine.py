from collections import deque

from turingarena.protocol.server.commands import ProxyRequest
from turingarena.protocol.server.frames import Frame, StatementContext, Phase, logger, RootBlockContext


class InterfaceEngine:
    def __init__(self, *, interface, proxy_connection, process_connection):
        self.interface = interface
        self.proxy_connection = proxy_connection
        self.process_connection = process_connection

        self.root_frame = Frame(parent=None, scope=interface.body.scope)
        self.callback_queue = deque()
        self.next_request = None
        self.input_sent = False

        self.main_block_context = RootBlockContext()
        self.run_generator = self.interface.run(self.new_context(
            root_block_context=self.main_block_context,
            phase=Phase.RUN,
        ))

    def run(self):
        next(self.interface.run(self.new_context(
            root_block_context=self.main_block_context,
            phase=Phase.PREFLIGHT,
        )))

    def new_context(self, *, root_block_context, phase):
        return StatementContext(
            engine=self,
            root_block_context=root_block_context,
            frame=self.root_frame,
            phase=phase,
        )

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
