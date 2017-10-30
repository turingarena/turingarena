import logging
import os
import sys
import tempfile
from contextlib import ExitStack

from turingarena.sandbox.client import Process

logger = logging.getLogger(__name__)


class PlumberServer:
    def __init__(self, *, protocol, interface_name, sandbox_dir):
        self.protocol = protocol
        self.interface = protocol.body.scope.interfaces[interface_name]

        self.main = self.interface.body.scope.main["main"]

        with ExitStack() as stack:
            prefix = "turingarena_plumber"
            plumber_dir = stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix))

            request_pipe_name = os.path.join(plumber_dir, "plumbing_request.pipe")
            response_pipe_name = os.path.join(plumber_dir, "plumbing_response.pipe")

            logger.debug("creating request/response pipes...")
            os.mkfifo(request_pipe_name)
            os.mkfifo(response_pipe_name)

            print(plumber_dir)
            sys.stdout.close()

            logger.debug("opening request pipe...")
            self.request_pipe = stack.enter_context(open(request_pipe_name))
            logger.debug("opening response pipe...")
            self.response_pipe = stack.enter_context(open(response_pipe_name, "w"))
            logger.debug("pipes opened")

            logger.debug("connecting to process...")
            self.connection = stack.enter_context(Process(sandbox_dir).connect())
            logger.debug("connected")

            self.plumbing = self.make_plumbing()
            self.input_sent = False
            self.run()

    def make_plumbing(self):
        yield from self.plumb_body(self.main.body)
        yield

    def plumb_body(self, body):
        for statement in body.statements:
            yield from self.plumb_statement(statement)

    def plumb_statement(self, statement):
        logger.debug("plumbing {}".format(statement))
        plumbers = {
            "input": self.plumb_input,
            "output": self.plumb_input,
            "flush": self.plumb_flush,
        }
        plumber = plumbers.get(statement.statement_type, None)
        if plumber:
            yield from plumber(statement)
        yield from []

    def plumb_input(self, statement):
        yield from []

    def plumb_output(self, statement):
        yield from []

    def plumb_flush(self, statement):
        yield

    def run(self):
        logger.debug("reading global variables")
        command = self.receive()
        assert command == "globals"
        for variable in self.interface.body.scope.variables.values():
            logger.debug("reading global variable {}".format(variable.name))
            variable.type.deserialize(file=self.connection.request_pipe)

        logger.debug("starting main procedure")

        self.run_body(self.main.body)

    def run_body(self, body):
        for statement in body.statements:
            self.run_statement(statement)

    def run_statement(self, statement):
        runners = {
            "call": self.run_call,
        }
        runner = runners.get(statement.statement_type, None)
        if runner:
            runner(statement)
        else:
            logger.debug("ignoring statement {}".format(statement))

    def receive(self):
        logger.debug("receiving request")
        line = self.request_pipe.readline().strip()
        logger.debug("received request '{}'".format(line))
        return line

    def send(self, line):
        logger.debug("sending response '{}'".format(line))
        print(line, file=self.response_pipe)

    def run_call(self, statement):
        logger.debug("expecting call {}...".format(statement))
        command = self.receive()
        assert command == "call"
        function_name = self.receive()
        assert function_name == statement.function_name
        has_callbacks = bool(self.receive())

        logger.debug("received call command (has_callbacks={has_callbacks})".format(
            has_callbacks=has_callbacks,
        ))

        arg_values = [
            self.deserialize(arg.type)
            for arg in statement.function.declarator.parameters
        ]

        logger.debug("arguments = {}".format(arg_values))

        if has_callbacks or statement.function.declarator.return_type:
            self.maybe_advance_plumbing()

    def maybe_advance_plumbing(self):
        if not self.input_sent:
            self.advance_plumbing()
        self.input_sent = True

    def advance_plumbing(self):
        next(self.plumbing)
