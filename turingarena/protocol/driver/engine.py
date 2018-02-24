from collections import deque

from turingarena.protocol.driver.commands import ProxyRequest
from turingarena.protocol.driver.frames import Frame, StatementContext, Phase, logger, RootBlockContext
from turingarena.protocol.exceptions import ProtocolError


class InterfaceEngine:
    def __init__(self, *, interface, driver_connection, sandbox_connection):
        self.interface = interface
        self.driver_connection = driver_connection
        self.sandbox_connection = sandbox_connection

        self.root_frame = Frame(parent=None, scope=interface.body.scope)
        self.callback_queue = deque()
        self._current_request = None
        self.input_sent = False

        self.main_block_context = RootBlockContext()
        self.run_generator = self.interface.run(self.new_context(
            root_block_context=self.main_block_context,
            phase=Phase.RUN,
        ))

    def run(self):
        generator = self.interface.run(self.new_context(
            root_block_context=self.main_block_context,
            phase=Phase.PREFLIGHT,
        ))
        l = list(generator)
        # in the preflight phase, the protocol should never yield
        assert l == []

    def new_context(self, *, root_block_context, phase):
        return StatementContext(
            engine=self,
            root_block_context=root_block_context,
            frame=self.root_frame,
            phase=phase,
        )

    def peek_request(self, **kwargs):
        self._ensure_current_request()
        self._validate_current_request(**kwargs)
        return self._current_request

    def process_request(self, **kwargs):
        self._ensure_current_request()
        self._validate_current_request(**kwargs)
        return self._pop_current_request()

    def _ensure_current_request(self):
        if self._current_request is not None:
            return
        self._current_request = ProxyRequest.accept(
            map(str.strip, self.driver_connection.request),
            interface_signature=self.interface.signature,
        )

    def _validate_current_request(self, *, expected_type=None):
        r = self._current_request
        if expected_type is not None:
            if r.message_type != expected_type:
                raise ProtocolError(f"expecting '{expected_type}', got '{r.message_type}'")

    def _pop_current_request(self):
        try:
            return self._current_request
        finally:
            self._current_request = None

    def send_response(self, response):
        file = self.driver_connection.response
        for line in response.serialize():
            print(line, file=file)
        file.flush()

    def ensure_output(self):
        logger.debug("ensure_output")
        if not self.input_sent:
            logger.debug("starting communication block")
            try:
                next(self.run_generator)
            except StopIteration as e:
                # avoid StopIteration exceptions to propagate and cause a mess
                raise AssertionError(e)
            logger.debug("communication block ended")
        self.input_sent = True

    def flush(self):
        assert self.input_sent
        self.input_sent = False

    def push_callback(self, callback):
        self.callback_queue.append(callback)

    def pop_callback(self):
        return self.callback_queue.popleft()
