import logging
import os
import subprocess
from contextlib import contextmanager, ExitStack

from turingarena.protocol.connection import ProxyConnection
from turingarena.protocol.model.exceptions import ProtocolError
from turingarena.protocol.module import ProtocolModule
from turingarena.protocol.server.commands import FunctionCall, CallbackReturn, ProxyResponse, MainBegin, MainEnd

logger = logging.getLogger(__name__)


class ProxyClient:
    def __init__(self, *, protocol_name, interface_name, process):
        self.protocol_name = protocol_name
        self.interface_name = interface_name
        self.process = process

    @contextmanager
    def connect(self):
        cli = [
            f"turingarena",
            f"protocol",
            f"--name={self.protocol_name}",
            f"server",
            f"--interface={self.interface_name}",
            f"--sandbox={self.process.sandbox_dir}",
        ]
        with ExitStack() as stack:
            logger.debug(f"running {cli}...")
            proxy_process = subprocess.Popen(
                cli,
                stdout=subprocess.PIPE,
                universal_newlines=True,
            )
            stack.enter_context(proxy_process)
            proxy_dir = proxy_process.stdout.readline().strip()
            logger.debug(f"proxy dir: {proxy_dir}...")

            assert os.path.isdir(proxy_dir)

            logger.debug("opening request pipe...")
            request_pipe = stack.enter_context(open(proxy_dir + "/proxy_request.pipe", "w"))
            logger.debug("opening response pipe...")
            response_pipe = stack.enter_context(open(proxy_dir + "/proxy_response.pipe"))
            logger.debug("proxy connected")

            try:
                yield ProxyConnection(
                    request_pipe=request_pipe,
                    response_pipe=response_pipe,
                )
            except Exception as e:
                logger.exception(e)
                raise

            logger.debug("waiting for proxy server process")


class ProxiedAlgorithm:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.protocol_name = self.algorithm.source.protocol_name
        self.interface_name = self.algorithm.source.interface_name

    @contextmanager
    def run(self, **global_variables):
        protocol_module = ProtocolModule(name=self.protocol_name)

        interface_signature = protocol_module.load_interface_signature(self.interface_name)
        sandbox = self.algorithm.executable.sandbox()
        with sandbox.run() as process:
            proxy = ProxyClient(
                protocol_name=self.protocol_name,
                interface_name=self.interface_name,
                process=process,
            )
            with proxy.connect() as connection:
                engine = ProxyEngine(
                    connection=connection,
                    interface_signature=interface_signature,
                )
                engine.begin_main(**global_variables)
                yield Proxy(engine=engine, interface_signature=interface_signature)
                engine.end_main()


class ProxyException(Exception):
    pass


class ProxyEngine:
    def __init__(self, *, interface_signature, connection):
        self.interface_signature = interface_signature
        self.connection = connection

    def call(self, name, args, callbacks_impl):
        try:
            function_signature = self.interface_signature.functions[name]
        except KeyError:
            raise ProtocolError(f"undefined function {name}")

        if len(args) != len(function_signature.parameters):
            raise ProtocolError(
                f"function '{name}'"
                f" expects {len(function_signature.parameters)} parameters,"
                f" got {len(args)}")

        request = FunctionCall(
            interface_signature=self.interface_signature,
            function_name=name,
            parameters=[
                p.value_type.ensure(a)
                for p, a in zip(function_signature.parameters, args)
            ],
            accept_callbacks=bool(callbacks_impl),
        )
        self.send(request)

        while True:
            logger.debug("waiting for response...")
            response = self.accept_response()
            if response.message_type == "callback_call":
                callback_name = response.callback_name
                callback_signature = self.interface_signature.callbacks[callback_name]
                raw_return_value = callbacks_impl[callback_name](*response.parameters)
                return_type = callback_signature.return_type
                if return_type:
                    return_value = return_type.ensure(raw_return_value)
                else:
                    assert raw_return_value is None
                    return_value = None
                request = CallbackReturn(
                    interface_signature=self.interface_signature,
                    callback_name=callback_name,
                    return_value=return_value,
                )
                self.send(request)
                continue
            if response.message_type == "function_return":
                return response.return_value

    def accept_response(self):
        return ProxyResponse.accept(
            map(str.strip, self.connection.response_pipe),
            interface_signature=self.interface_signature,
        )

    def send(self, request):
        file = self.connection.request_pipe
        for line in request.serialize():
            print(line, file=file)
        file.flush()

    def begin_main(self, **global_variables):
        request = MainBegin(
            interface_signature=self.interface_signature,
            global_variables=[
                global_variables[variable.name]
                for variable in self.interface_signature.variables.values()
            ]
        )
        self.send(request)

    def end_main(self):
        request = MainEnd(
            interface_signature=self.interface_signature,
        )
        self.send(request)


class Proxy:
    def __init__(self, engine, interface_signature):
        self._engine = engine
        self._interface_signature = interface_signature

    def __getattr__(self, item):
        try:
            fun = self._interface_signature.functions[item]
        except KeyError:
            raise AttributeError

        def method(*args, **kwargs):
            return self._engine.call(item, args=args, callbacks_impl=kwargs)

        return method
