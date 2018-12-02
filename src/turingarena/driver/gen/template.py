from turingarena.driver.common.nodes import Block
from turingarena.driver.gen.nodes import InterfaceTemplate, MethodTemplate, Comment


def interface_template(n, descriptions):
    if descriptions is None:
        descriptions = {}

    return InterfaceTemplate(
        constants=n.constants,
        methods=tuple(
            MethodTemplate(
                prototype=m,
                description=descriptions.get(m.name),
                body=Block((Comment("TODO"),)),
            )
            for m in n.methods
        ),
    )
