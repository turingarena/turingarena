from collections import namedtuple

scalar = namedtuple("scalar", ["base_type"])
array = namedtuple("array", ["item_type"])

arg = namedtuple("arg", ["type", "name"])
signature = namedtuple("signature", ["name", "arguments", "return_type"])
interface_function = namedtuple("interface_function", ["signature"])
interface_callback = namedtuple("interface_callback", ["signature"])
interface_var = namedtuple("interface_var", ["type", "names"])


class ProxyException(Exception):
    pass


class ProxyEngine:
    def __init__(self, *, interface, instance, connection):
        self.interface = interface
        self.instance = instance
        self.connection = connection

        self.functions = {
            s.signature.name: s for s in interface if isinstance(s, interface_function)
        }
        self.callbacks = {
            s.signature.name: s for s in interface if isinstance(s, interface_callback)
        }

        self.globals_sent = False

    def send(self, value, *, indent=0):
        assert indent <= 10
        print("  " * indent, value, sep="", file=self.connection.request_pipe)

    def receive(self):
        return self.connection.response_pipe.readline().strip()

    def serialize(self, value, *, type_expression, indent=0):
        if isinstance(type_expression, scalar):
            assert isinstance(value, type_expression.base_type)
            self.send(value, indent=indent)
        elif isinstance(type_expression, array):
            value = list(value)
            self.send(len(value), indent=indent)
            for item in value:
                self.serialize(
                    item,
                    type_expression=type_expression.item_type,
                    indent=indent + 1,
                )
        else:
            raise AssertionError

    def deserialize(self, type_expression):
        assert isinstance(type_expression, scalar)
        return type_expression.base_type(self.receive())

    def flush(self):
        self.connection.request_pipe.flush()

    def call(self, name, args, callbacks_impl):
        if not self.globals_sent:
            self.send_globals()
        self.globals_sent = True

        fun = self.functions[name]
        signature = fun.signature

        self.send("call")
        self.send(signature.name)
        self.send(1 if callbacks_impl else 0)

        for arg, value in zip(signature.arguments, args):
            self.serialize(value, type_expression=arg.type)

        self.flush()

        if callbacks_impl:
            self.accept_callbacks(callbacks_impl)

        status = self.receive()
        assert status == "function_stop"

        if signature.return_type:
            return self.accept_return_value(signature.return_type)


    def accept_callbacks(self, callbacks_impl):
        while True:
            status = self.receive()
            if status == "callback":
                name = self.receive()
                callback = self.callbacks[name]
                try:
                    impl = callbacks_impl[name]
                except KeyError:
                    raise ProxyException("unexpected callback")
                self.accept_callback(callback, impl)
            elif status == "no_callbacks":
                break
            else:
                raise ProxyException("unexpected status", status)

    def accept_callback(self, callback, impl):
        signature = callback.signature
        values = [
            self.deserialize(a.type)
            for a in signature.arguments
        ]
        ret = impl(*values)
        self.send("callback_stop")
        if signature.return_type:
            self.send("callback_return")
            self.serialize(ret, type_expression=signature.return_type)
        self.flush()

    def accept_return_value(self, return_type):
        status = self.receive()
        if status == "function_return":
            return self.deserialize(return_type)
        else:
            raise ProxyException("unexpected status", status)

    def send_globals(self):
        self.send("globals")
        for s in self.interface:
            if not isinstance(s, interface_var): continue
            for name in s.names:
                value = getattr(self.instance, name)
                self.serialize(value, type_expression=s.type)
