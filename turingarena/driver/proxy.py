class MethodProxy:
    def __init__(self, engine, has_return_value):
        self._engine = engine
        self._has_return_value = has_return_value

    def __getattr__(self, item):
        def method(*args, callbacks):
            return self._engine.call(
                item,
                arguments=args,
                has_return_value=self._has_return_value,
                callbacks=callbacks,
            )

        return method
