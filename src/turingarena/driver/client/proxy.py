from functools import partial


class MethodProxy:
    def __init__(self, process, has_return_value):
        self._process = process
        self._has_return_value = has_return_value

    def __getattr__(self, item):
        return partial(self._process.call, item, has_return_value=self._has_return_value)
