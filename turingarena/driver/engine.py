import logging
from collections import namedtuple

from turingarena.driver.commands import serialize_data


class DriverClientEngine(namedtuple("DriverClientEngine", ["connection"])):
    def call(self, name, *, arguments, has_return_value, callbacks):
        self.send_call(arguments, name, has_return_value, callbacks)

        if callbacks:
            self.connection.downward.flush()
            self.accept_callbacks(callbacks)

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
                logging.debug(f"has callback")
                index = self.get_response_line()
                callback = callback_list[index]
                args = [
                    int(self.get_response_line())
                    for _ in range(callback.__code__.co_argcount)
                ]
                return_value = callback(*args)
                logging.debug(f"callback {index} ({args}) -> {return_value}")
                self.send_callback_return(return_value)
            else:  # no callbacks
                break

    def send_call(self, args, name, has_return_value, callbacks):
        return self.send_request([
            "call",
            name,
            len(args),
            *[
                l
                for a in args
                for l in serialize_data(a)
            ],
            int(has_return_value),
            len(callbacks),
            *[
                c.__code__.co_argcount
                for c in callbacks
            ],
        ])

    def send_callback_return(self, return_value):
        request = ["callback_return"]
        if return_value is not None:
            request += [1, return_value]
        else:
            request += [0]
        return self.send_request(request)

    def send_exit(self):
        return self.send_request(["exit"])

    def send_request(self, lines):
        for line in lines:
            logging.debug(f"sending request line: {line}")
            print(line, file=self.connection.downward)
        self.connection.downward.flush()  # FIXME: should not be needed
