from turingarena.driver.interface.nodes import IntermediateNode


class SequenceNode(IntermediateNode):

    def _get_reference_actions(self):
        for n in self.children:
            yield from n.reference_actions

    def validate(self):
        for n in self.children:
            yield from n.validate()
