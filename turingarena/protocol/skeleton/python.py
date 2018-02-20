import os

from turingarena.common import write_to_file, indent_all, indent

def generate_skeleton(*, interface, dest_dir):
    with open(os.path.join(dest_dir, "skeleton.py"), "w") as main_file:
        write_to_file(generate_main_file(interface), main_file)
    with open(os.path.join(dest_dir, "source.py"), "w") as template_file:
        write_to_file(generate_template_file(interface), template_file)


def generate_main_file(interface):
    yield "import sys"
    for statement in interface.body.statements:
        yield
        yield from generate_skeleton_statement(statement, interface=interface)


def generate_template_file(interface):
    for statement in interface.body.statements:
        yield
        yield from generate_template_statement(statement, interface=interface)

def generate_skeleton_statement(statement, *, interface):
    generators = {
        "var": lambda: generate_var(statement),
        "function": lambda: [],
        "callback": lambda: generate_callback(statement, interface=interface),
        "main": lambda: generate_main(statement, interface=interface),
    }

    return generators[statement.statement_type]()


def generate_template_statement(statement, *, interface):
    generators = {
        "var": lambda: [generate_global_var_template(statement)],
        "function": lambda: generate_function_template(statement),
        "callback": lambda: generate_callback_template(statement, interface=interface),
        "main": lambda: [],
    }
    return generators[statement.statement_type]()


def generate_var(statement):
    names = ", ".join(d.name for d in statement.variables)
    nones = ", ".join("None" for _ in statement.variables)
    yield f"[{names}] = [{nones}]"


def generate_global_var_template(statement):
    names = ", ".join(v.name for v in statement.variables)
    yield f"from __main__ import {names}"


def generate_function_template(statement):
    function = statement.function
    yield f"def {build_callable_declarator(function)}:"
    yield indent("# TODO")
    yield indent("pass")


def generate_callback(statement, *, interface):
    callback = statement.callback
    yield f"def {build_callable_declarator(callback)}:"
    yield indent(f"print ('{callback.name}')")
    yield from indent_all(generate_block(callback.body, interface=interface))


def generate_callback_template(statement, *, interface):
    callback = statement.callback
    yield f"from __name__ import {callback.name}"


def generate_main(statement, *, interface):
    yield 'if __name__ == "__main__":'
    yield from indent_all(generate_block(statement.main.body, interface=interface))


def generate_block(block, *, interface):
    for statement in block.statements:
        yield from generate_block_statement(statement, interface=interface)


def generate_block_statement(statement, *, interface):
    generators = {
        "var": lambda: generate_var(statement),
        "alloc": lambda: generate_alloc(statement),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "flush": lambda: ["sys.stdout.flush()"],
        "call": lambda: generate_call(statement, interface=interface),
        "for": lambda: generate_for(statement, interface=interface),
        "if": lambda: generate_if(statement, interface=interface),
        "exit": lambda: ["sys.exit(0)"],
        "return": lambda: [f"return {build_expression(statement.value)}"],
    }
    return generators[statement.statement_type]()


def generate_alloc(statement):
    for argument in statement.arguments:
        arg = build_expression(argument)
        size = build_expression(statement.size)
        yield f"{arg} = [None] * {size}"


def generate_call(statement, *, interface):
    yield f"import source"
    function_name = statement.function.name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = source.{function_name}({parameters})"
    else:
        yield f"{function_name}({parameters})"
    if interface.signature.callbacks:
        yield r"""print("return")"""


def generate_output(statement):
    format_string = ' '.join('{}' for v in statement.arguments)
    args = ', '.join(build_expression(v) for v in statement.arguments)
    yield f'print("{format_string}".format({args}))'


def generate_input(statement):
    for v in statement.arguments:
        arg = build_expression(v)
        format_string = build_format(v)
        yield f'{arg} = {format_string}(input())'


def generate_if(statement, *, interface):
    condition = build_expression(statement.condition)
    yield f"if {condition} :"
    yield from indent_all(generate_block(statement.then_body, interface=interface))
    if statement.else_body is not None:
        yield "else:"
        yield from indent_all(generate_block(statement.else_body, interface=interface))


def generate_for(statement, *, interface):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for {index_name} in range({size}):"
    yield from indent_all(generate_block(statement.body, interface=interface))


def build_callable_declarator(callable):
    signature = callable.signature
    arguments = ', '.join(build_parameter(p) for p in signature.parameters)
    return f"{callable.name}({arguments})"


def build_parameter(parameter):
    return f'{parameter.name}'


def build_subscript(expression):
    array = build_expression(expression.array)
    index = build_expression(expression.index)
    return f"{array}[{index}]"


def build_expression(expression):
    builders = {
        "int_literal": lambda: f"{expression.value}",
        "reference": lambda: f"{expression.variable.name}",
        "subscript": lambda: build_subscript(expression),
    }
    return builders[expression.expression_type]()


def build_format(expr):
    return {
        int: "int",
    }[expr.value_type.base_type]
