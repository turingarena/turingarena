import itertools
import logging
from collections import namedtuple

from turingarena_impl.interface.exceptions import CommunicationBroken

logger = logging.getLogger(__name__)


def drive_interface(*, interface, sandbox_connection):
    # maintain two "instruction pointers" in the form of parallel iterators
    # over the same sequence of instructions (see itertools.tee).
    # driver_iterator is for handling driver requests (function call, callback return and exit)
    # sandbox_iterator is for communicating with sandbox (read/write)
    driver_iterator, sandbox_iterator = itertools.tee(
        interface.generate_instructions()
    )

    # a generator that executes the instructions in sandbox_iterator
    # and yields exactly once per communication block
    # (once for each yield instruction, and once at the end)
    run_sandbox_iterator = run_sandbox(sandbox_iterator, sandbox_connection=sandbox_connection)

    # a generator that receives driver requests
    # and yields responses
    return run_driver(driver_iterator, run_sandbox_iterator=run_sandbox_iterator)


def run_driver(driver_iterator, *, run_sandbox_iterator):
    current_request = None
    input_sent = False
    last_upward = False

    for instruction in driver_iterator:
        logger.debug(f"control: processing instruction {type(instruction)}")
        if current_request is None:
            current_request = yield
            assert current_request is not None

        instruction.on_request_lookahead(current_request)
        if instruction.should_send_input() and not input_sent:
            logger.debug(f"control: advancing communication block")
            # advance fully the current communication block
            next(run_sandbox_iterator)
            input_sent = True

        response = instruction.on_generate_response()
        if response is not None:
            assert (yield response) is None
            current_request = None

        if instruction.has_upward():
            last_upward = True

        if last_upward and instruction.has_downward():
            last_upward = False
            assert input_sent
            input_sent = False

        logger.debug(f"control: instruction {type(instruction)} processed")

        # assert input_sent


def send_response(driver_connection, response):
    for item in response:
        assert isinstance(item, (int, bool))
        print(int(item), file=driver_connection.response)
    driver_connection.response.flush()


def upward_reader(sandbox_connection):
    while True:
        try:
            sandbox_connection.downward.flush()
        except BrokenPipeError:
            raise CommunicationBroken

        line = sandbox_connection.upward.readline()
        if not line:
            raise CommunicationBroken
        yield tuple(map(int, line.strip().split()))


class DownwardWriter(namedtuple("DownwardWriter", ["sandbox_connection"])):
    def send(self, values):
        try:
            logger.debug(f"DOWNWARD: {values}")
            print(*values, file=self.sandbox_connection.downward)
        except BrokenPipeError:
            raise CommunicationBroken


def run_sandbox(instructions, *, sandbox_connection):
    last_upward = False
    upward_lines = upward_reader(sandbox_connection)
    downward_lines = DownwardWriter(sandbox_connection)

    for instruction in instructions:
        logger.debug(f"communication: processing instruction {type(instruction)}")

        if instruction.has_upward():
            instruction.on_communicate_upward(upward_lines)
            last_upward = True
        else:
            assert instruction.on_communicate_upward(upward_lines) is NotImplemented

        if instruction.has_downward():
            if last_upward:
                yield
            last_upward = False
            instruction.on_communicate_downward(downward_lines)
        else:
            assert instruction.on_communicate_downward(downward_lines) is NotImplemented

        logger.debug(f"communication: instruction {type(instruction)} processed")
    yield
