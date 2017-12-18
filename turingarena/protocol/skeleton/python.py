import os

from turingarena.common import write_to_file, indent_all, indent

template_file_name = "template"
def generate_skeleton(*, interface, dest_dir):
    with open(os.path.join(dest_dir, "skeleton.py"), "w") as main_file:
        write_to_file(generate_main_file(interface), main_file)
    with open(os.path.join(dest_dir, template_file_name+".py"), "w") as template_file:
        write_to_file(generate_template_file(interface), template_file)


def generate_main_file(interface):
    yield "import sys"
    yield "import " + template_file_name
    for statement in interface.body.statements:
        yield
        yield from generate_skeleton_statement(statement, interface=interface)


def generate_template_file(interface):
    for statement in interface.body.statements:
        yield
        yield from generate_template_statement(statement, interface=interface)

global_variable = []

def generate_skeleton_statement(statement, *, interface):
    generators = {
        "var": lambda: [],
        "function": lambda: generate_function(statement),
        "callback": lambda: generate_callback(statement, interface=interface),
        "main": lambda: generate_main(statement, interface=interface),
    }
    if statement.statement_type == "var":
        for variable in statement.variables:
            global_variable.append(variable.name)

    return generators[statement.statement_type]()


def generate_template_statement(statement, *, interface):
    generators = {
        "var": lambda: [build_declaration(statement)],
        "function": lambda: generate_function_template(statement),
        "callback": lambda: generate_callback_template(statement, interface=interface),
        "main": lambda: [],
    }
    return generators[statement.statement_type]()


def generate_function(statement):
    yield f"from template import {statement.function.name}"


def generate_function_template(statement):
    function = statement.function
    yield f"{build_callable_declarator(function)}:"
    yield indent("# TODO")
    yield indent("pass")


def generate_callback(statement, *, interface):
    callback = statement.callback
    yield f"{build_callable_declarator(callback)}:"
    yield indent(f"print ('{callback.name}')")
    yield from indent_all(generate_block(callback.body, interface=interface))


def generate_callback_template(statement, *, interface):
    callback = statement.callback
    yield f"from skeleton import {callback.name}"


def generate_main(statement, *, interface):
    yield 'if __name__ == "__main__":'
    yield from indent_all(generate_block(statement.main.body, interface=interface))


def generate_block(block, *, interface):
    for statement in block.statements:
        yield from generate_block_statement(statement, interface=interface)


def generate_block_statement(statement, *, interface):
    generators = {
        "var": lambda: [],
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


def generate_declarators(declaration):
    for variable in declaration.variables:
        yield build_declarator(declaration.value_type, variable.name)


def generate_alloc(statement):
    for argument in statement.arguments:
        arg = build_expression(argument)
        size = build_expression(statement.size)
        yield f"{arg} = [None]*{size}"


def generate_call(statement, *, interface):
    function_name = statement.function.name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = template.{function_name}({parameters})"
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
    yield f"for {index_name} in range(0,{size}):"
    yield from indent_all(generate_block(statement.body, interface=interface))


def build_callable_declarator(callable):
    signature = callable.signature
    arguments = ', '.join(build_parameter(p) for p in signature.parameters)
    return f"def {callable.name}({arguments})"


def build_declaration(statement):
    declarators = ', '.join(generate_declarators(statement))
    return f'{declarators}'


def build_parameter(parameter):
    declarator = build_declarator(parameter.value_type, parameter.name)
    return f'{declarator}'


def build_subscript(expression):
    array = build_expression(expression.array)
    index = build_expression(expression.index)
    return f"{array}[{index}]"


def build_expression(expression):
    builders = {
        "int_literal": lambda: f"{expression.value}",
        "reference": lambda: generate_variable(expression),
        "subscript": lambda: build_subscript(expression),
    }
    return builders[expression.expression_type]()

def generate_variable(expression):
    if expression.variable.name in global_variable:
        return f"template.{expression.variable.name}"
    else:
        return f"{expression.variable.name}"


def build_declarator(value_type, name):
    if value_type is None:
        return name
    builders = {
        "scalar": lambda: name,
        "array": lambda: name,
    }
    return builders[value_type.meta_type]()

def build_format(expr):
    return {
        int: "int",
    }[expr.value_type.base_type]
