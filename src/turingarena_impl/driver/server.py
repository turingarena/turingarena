import logging
import sys
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena.algorithm import Program
from turingarena.driver.connection import DriverProcessConnection
from turingarena_impl.driver.interface.exceptions import CommunicationError
from turingarena_impl.driver.interface.execution import NodeExecutionContext, ProcessExplicitlyKilled
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language

logger = logging.getLogger(__name__)


def main():
    _, source_path, interface_path = sys.argv

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
        except CommunicationError as e:
            context.send_driver_upward(-1)  # error
            info = context.perform_wait(kill_reason="communication error")
            message, = e.args
            context.send_driver_upward(f"{message} (process {info.error})")
        except ProcessExplicitlyKilled:
            logger.debug("process killed")


if __name__ == '__main__':
    main()
