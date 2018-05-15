class InterfaceProxy:
    def __init__(self, running_process):
        self._running_process = running_process

    def __getattr__(self, item):
        def method(*args):
            return self._running_process.call(item, args)

        return method
