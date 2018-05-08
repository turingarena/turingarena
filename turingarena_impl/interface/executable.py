from abc import abstractmethod, ABC

from turingarena_impl.interface.statement import Statement


class Instruction:
    __slots__ = []

    def on_request_lookahead(self, request):
        pass

    def on_generate_response(self):
        pass

    def on_communicate_with_process(self, connection):
        pass

    def should_send_input(self):
        return False

    def is_flush(self):
        return False


class ImperativeStructure(ABC):
    __slots__ = []

    @abstractmethod
    def generate_instructions(self, context):
        pass

    @abstractmethod
    def expects_request(self, request):
        pass

    @property
    @abstractmethod
    def context_after(self):
        pass


class ImperativeStatement(Statement, ImperativeStructure):
    __slots__ = []

    def expects_request(self, request):
        if request is None:
            return True
        return False

    @property
    def variables_to_declare(self):
        return tuple(
            var
            for var in self.declared_variables
            if var.to_allocate == 0
        )

    @property
    def declared_variables(self):
        return ()

    @property
    def variables_to_allocate(self):
        return ()
