from collections import namedtuple

import logging

from turingarena.driver.commands import MethodCall, CallbackReturn, Exit, serialize_request


class DriverClientEngine(namedtuple("DriverClientEngine", ["connection"])):
    def call(self, name, *, args, has_return_value, callbacks):
        callback_list = list(callbacks.items())

        self.send_call(args, name, has_return_value, callback_list)

        if callback_list:
            self.connection.downward.flush()
            self.accept_callbacks(callback_list)

        if has_return_value:
            self.connection.downward.flush()
            return self.receive_return_value()
        else:
            return None

    def receive_return_value(self):
        logging.debug(f"Receiving return value...")
        return int(self.connection.upward.readline())

    def get_response_line(self):
        line = self.connection.upward.readline().strip()
        assert line
        logging.debug(f"Read response line: {line}")
        return int(line)

    def accept_callbacks(self, callback_list):
        while True:
            if self.get_response_line():  # has callback
                index = self.get_response_line()
                # FIXME:
                # args = list(response_it)
                args = []
                name, f = callback_list[index]
                return_value = f(*args)
                self.send_callback_return(return_value)
            else:  # no callbacks
                break

    def send_call(self, args, name, has_return_value, callback_list):
        return self.send_request(MethodCall(
            method_name=name,
            parameters=args,
            has_return_value=has_return_value,
            accepted_callbacks={
                name: f.__code__.co_argcount
                for name, f in callback_list
            },
        ))

    def send_callback_return(self, return_value):
        return self.send_request(CallbackReturn(return_value=return_value))

    def send_exit(self):
        return self.send_request(Exit())

    def send_request(self, request):
        for l in serialize_request(request):
            print(l, file=self.connection.downward)
        self.connection.downward.flush()  # FIXME: should not be needed
