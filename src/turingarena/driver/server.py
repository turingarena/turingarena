import logging
import sys
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena.cli.common import init_logger
from turingarena.driver.client.commands import DriverState
from turingarena.driver.client.connection import DriverProcessConnection
from turingarena.driver.client.program import Program
from turingarena.driver.compile.compile import load_interface
from turingarena.driver.drive.comm import CommunicationError, DriverStop, InterfaceExitReached, SandboxTee
from turingarena.driver.drive.execution import Executor
from turingarena.driver.language import Language

logger = logging.getLogger(__name__)


def main():
    _, source_path, interface_path, downward_tee, upward_tee = sys.argv

    init_logger()

    run_server(DriverProcessConnection(
        downward=sys.stdin,
        upward=sys.stdout,
    ), source_path, interface_path, downward_tee, upward_tee)


def run_server(driver_connection, source_path, interface_path, downward_tee, upward_tee):
    program = Program(source_path=source_path, interface_path=interface_path)
    language = Language.from_source_path(program.source_path)
    interface = load_interface(program.interface_path)

    with ExitStack() as stack:
        temp_dir = stack.enter_context(TemporaryDirectory())

        runner = language.ProgramRunner(
            program=program,
            language=language,
            interface=interface,
            temp_dir=temp_dir,
        )

        connection = stack.enter_context(runner.run_in_process())

        sandbox_tee = SandboxTee(
            downward_tee=stack.enter_context(open(downward_tee, "w")),
            upward_tee=stack.enter_context(open(upward_tee, "w")),
        )

        stack.callback(lambda: connection.manager.get_status(
            kill_reason="still running after communication end",
        ))

        context = Executor(
            bindings={},
            phase=None,
            process=connection.manager,
            request_lookahead=None,
            driver_connection=driver_connection,
            sandbox_connection=connection,
            sandbox_tee=sandbox_tee,
        )

        try:
            try:
                context.execute(interface)
            except InterfaceExitReached:
                pass
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
