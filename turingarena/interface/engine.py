import itertools
import logging

logger = logging.getLogger(__name__)


def drive_interface(*, interface, sandbox_connection):
    # maintain two "instruction pointers" in the form of paraller iterators
    # over the same sequence of instructions (see itertools.tee).
    # driver_iterator is for handling driver requests (main begin/end, function call, callback return and exit)
    # sandbox_iterator is for communicating with sandbox (input/output)
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

    for instruction in driver_iterator:
        if current_request is None:
            current_request = yield
            assert current_request is not None

        instruction.on_request_lookahead(current_request)
        if instruction.should_send_input() and not input_sent:
            # advance fully the current communication block
            next(run_sandbox_iterator)
            input_sent = True

        response = instruction.on_generate_response()
        if response is not None:
            assert (yield response) is None
            current_request = None

        if instruction.is_flush():
            assert input_sent
            input_sent = False

    assert input_sent


def send_response(driver_connection, response):
    for item in response:
        assert isinstance(item, (int, bool))
        print(int(item), file=driver_connection.response)
    driver_connection.response.flush()


def run_sandbox(instructions, *, sandbox_connection):
    for instruction in instructions:
        instruction.on_communicate_with_process(sandbox_connection)
        if instruction.is_flush():
            yield
    yield
