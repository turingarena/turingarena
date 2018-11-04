import logging
import sys
from contextlib import ExitStack
from tempfile import TemporaryDirectory

from turingarena.algorithm import Program
from turingarena.driver.connection import DriverProcessConnection
from turingarena_impl.driver.interface.exceptions import CommunicationError
from turingarena_impl.driver.interface.execution import NodeExecutionContext, ProcessKilled
from turingarena_impl.driver.interface.interface import InterfaceDefinition
from turingarena_impl.driver.language import Language

logger = logging.getLogger(__name__)


def main():
    _, source_path, interface_path = sys.argv

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
            driver_connection=DriverProcessConnection(
                downward=sys.stdin,
                upward=sys.stdout,
            ),
            sandbox_connection=connection,
        )

        try:
            interface.run_driver(context)
        except CommunicationError as e:
            context.send_driver_upward(-1)  # error
            info = context.perform_wait(kill_reason="communication error")
            message, = e.args
            context.send_driver_upward(f"{message} (process {info.error})")
        except ProcessKilled:
            logger.debug("process killed")


class DriverProcessServer:
    def __init__(self, program: Program):
        self.program = program
        self.interface = InterfaceDefinition.load(program.interface_path)

        self.done = False
        self.process = None

        self.process_exit_stack = ExitStack()

    def run(self, connection):
        with self.process_exit_stack as stack:
            sandbox_connection = self.start_process_and_connect()

        logger.debug("process terminated")

    def start_process_and_connect(self):
        try:
            source, compilation_dir = self.compile_algorithm(self.program)
            if compilation_dir:
                self.process = source.create_process(compilation_dir)
            else:
                self.process = CompilationFailedProcessManager()
        except:
            logger.exception("exception while starting process")

    def compile_algorithm(self):
        if self.program.language_name is not None:
            language = Language.from_name(self.program.language_name)
        else:
            language = None
        interface = InterfaceDefinition.load(self.program.interface_path)
        source = AlgorithmSource.load(
            self.program.source_path,
            interface=interface,
            language=language,
        )
        try:
            with ExitStack() as exit:
                compilation_dir = exit.enter_context(TemporaryDirectory(prefix="turingarena_"))
                source.compile(compilation_dir)
                # if everything went ok, keep the temporary dir until we stop
                self.exit_stack.push(exit.pop_all())
        except CompilationFailed:
            return source, None
        else:
            return source, compilation_dir


if __name__ == '__main__':
    main()
