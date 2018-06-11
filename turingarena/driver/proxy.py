class FunctionProxy:
    def __init__(self, engine):
        self._engine = engine

    def __getattr__(self, item):
        def method(*args, **kwargs):
            return self._engine.call(item, args=args, has_return_value=True, callbacks=kwargs)

        return method


class ProcedureProxy:
    def __init__(self, engine):
        self._engine = engine

    def __getattr__(self, item):
        def method(*args, **kwargs):
            return self._engine.call(item, args=args, has_return_value=False, callbacks=kwargs)

        return method
