from collections import namedtuple

from turingarena.driver.commands import MethodCall, CallbackReturn, Exit, serialize_request


class DriverClientEngine(namedtuple("DriverClientEngine", ["connection"])):
    def call(self, name, *, args, has_return, callbacks):
        callback_list = list(callbacks.items())

        self.send_call(args, name, has_return, callback_list)

        if callback_list:
            self.connection.downward.flush()
            self.accept_callbacks(callback_list)

        if has_return:
            self.connection.downward.flush()
            return self.receive_return_value()
        else:
            return None

    def receive_return_value(self):
        return int(self.connection.upward.readline())

    def accept_callbacks(self, callback_list):
        raise NotImplementedError
        while True:
            response_it = self.response_iterator(response)
            if next(response_it):  # has callback
                index = next(response_it)
                args = list(response_it)
                name, f = callback_list[index]
                return_value = f(*args)
                response = self.send_callback_return(return_value)
            else:  # no callbacks
                break

    def send_call(self, args, name, has_return, callback_list):
        return self.send_request(MethodCall(method_name=name, parameters=args, accepted_callbacks={
            name: f.__code__.co_argcount
            for name, f in callback_list
        }))

    def send_callback_return(self, return_value):
        return self.send_request(CallbackReturn(return_value=return_value))

    def send_exit(self):
        return self.send_request(Exit())

    def send_request(self, request):
        for l in serialize_request(request):
            print(l, file=self.connection.downward)
        self.connection.downward.flush()  # FIXME: should not be needed

    def response_iterator(self, response):
        items = [int(line.strip()) for line in response.splitlines()]
        return iter(items)
