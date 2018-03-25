from collections import namedtuple


class AbstractSyntaxNodeWrapper(namedtuple("AbstractSyntaxNodeWrapper", ["ast", "context"])):
    __slots__ = []

    def check_variables(self, initialized_variables, allocated_variables):
        """
        Check that the variables used by this node where initialized
        :param initialized_variables: list of initialized variables
        :param allocated_variables: list of allocated variables
        :return:
        """
        return

    def initialized_variables(self):
        return []

    def allocated_variables(self):
        return []
