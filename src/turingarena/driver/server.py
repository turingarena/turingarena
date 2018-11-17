import logging
import sys
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena.cli.common import init_logger
from turingarena.driver.client.commands import DriverState
from turingarena.driver.client.connection import DriverProcessConnection
from turingarena.driver.client.program import Program
from turingarena.driver.interface.exceptions import CommunicationError, DriverStop
from turingarena.driver.interface.execution import NodeExecutionContext
from turingarena.driver.interface.interface import InterfaceDefinition
from turingarena.driver.language import Language

logger = logging.getLogger(__name__)


def main():
    _, source_path, interface_path = sys.argv

    init_logger()

    run_server(DriverProcessConnection(
        downward=sys.stdin,
        upward=sys.stdout,
    ), source_path, interface_path)


def run_server(driver_connection, source_path, interface_path):
    program = Program(source_path=source_path, interface_path=interface_path)
    language = Language.from_source_path(program.source_path)
    interface = InterfaceDefinition.load(program.interface_path)

    with ExitStack() as stack:
        temp_dir = stack.enter_context(TemporaryDirectory())

        runner = language.ProgramRunner(
            program=program,
            language=language,
            interface=interface,
            temp_dir=temp_dir,
        )

        connection = stack.enter_context(runner.run_in_process())

        stack.callback(lambda: connection.manager.get_status(
            kill_reason="still running after communication end",
        ))

        context = NodeExecutionContext(
            bindings={},
            phase=None,
            direction=None,
            process=connection.manager,
            request_lookahead=None,
            driver_connection=driver_connection,
            sandbox_connection=connection,
        )

        try:
            interface.run_driver(context)
            context.report_ready()
            request = context.next_request()
            assert False, f"driver was not explicitly stopped, got {request}"
        except CommunicationError as e:
            logging.debug(f"communication error", exc_info=True)
            context.send_driver_state(DriverState.ERROR)  # error
            info = connection.manager.get_status(kill_reason="communication error")
            message, = e.args
            context.send_driver_upward(f"{message} (process {info.error})")
        except DriverStop:
            context.send_driver_state(DriverState.READY)  # ok, no errors


if __name__ == '__main__':
    main()
