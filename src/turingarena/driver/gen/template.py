import logging

from turingarena.driver.common.nodes import Block
from turingarena.driver.gen.nodes import InterfaceTemplate, MethodTemplate, Comment
from turingarena.text.textgen import TextGenerator


def interface_template(n, descriptions):
    if descriptions is None:
        descriptions = {}

    textgen = TextGenerator()
    description_lines = {
        k: textgen.lines(v)
        for k, v in descriptions.items()
    }

    return InterfaceTemplate(
        constants=n.constants,
        methods=tuple(
            MethodTemplate(
                prototype=m,
                description=description_lines.get(m.name),
                body=Block((Comment("TODO"),)),
            )
            for m in n.methods
        ),
    )
