from turingarena.common import indent_all, indent


def generate_skeleton_cpp(interface):
    yield "#include <cstdio>"
    yield "#include <cstdlib>"
    for statement, context in interface.contextualized_statements():
        yield
        yield from generate_skeleton_statement(statement, context=context)
    yield
    yield from generate_main(interface)


def generate_template_cpp(interface):
    for statement, context in interface.contextualized_statements():
        yield
        yield from generate_template_statement(statement, context=context)


def generate_skeleton_statement(statement, *, context):
    generators = {
        "var": lambda: ["extern " + build_declaration(statement)],
        "function": lambda: generate_function(statement),
        "callback": lambda: generate_callback(statement, context=context),
        "init": lambda: [],
        "main": lambda: [],
    }
    return generators[statement.statement_type]()


def generate_template_statement(statement, *, context):
    generators = {
        "var": lambda: [build_declaration(statement)],
        "function": lambda: generate_function_template(statement),
        "callback": lambda: generate_callback_template(statement, context=context),
        "init": lambda: [],
        "main": lambda: [],
    }
    return generators[statement.statement_type]()


def generate_function(statement):
    yield f"{build_callable_declarator(statement.function)};"


def generate_function_template(statement):
    yield f"{build_callable_declarator(statement.function)}" " {"
    yield indent("// TODO")
    yield "}"


def generate_callback(statement, *, context):
    callback = statement.callback
    body, body_context = callback.contextualized_body(context)
    yield f"{build_callable_declarator(callback)}" " {"
    yield indent(rf"""printf("%s\n", "{callback.name}");""")
    yield from indent_all(generate_block(body, context=body_context))
    yield "}"


def generate_callback_template(statement, *, context):
    callback = statement.callback
    yield f"{build_callable_declarator(callback)};"


def generate_main(interface):
    yield "int main() {"
    for statement, context in interface.contextualized_statements():
        if statement.statement_type in ("init", "main"):
            body, body_context = statement.contextualized_body(context)
            yield from indent_all(generate_block(body, context=body_context))
    yield "}"


def generate_block(block, *, context):
    for statement, inner_context in block.contextualized_statements(context):
        yield from generate_block_statement(statement, context=inner_context)


def generate_block_statement(statement, *, context):
    generators = {
        "var": lambda: [build_declaration(statement)],
        "alloc": lambda: generate_alloc(statement, context=context),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "checkpoint": lambda: [r"""printf("%d\n", 0);"""],
        "flush": lambda: ["fflush(stdout);"],
        "call": lambda: generate_call(statement, context=context),
        "for": lambda: generate_for(statement, context=context),
        "if": lambda: generate_if(statement, context=context),
        "exit": lambda: ["exit(0);"],
        "return": lambda: [f"return {build_expression(statement.value)};"],
    }
    return generators[statement.statement_type]()


def generate_declarators(declaration):
    for variable in declaration.variables:
        yield build_declarator(declaration.value_type, variable.name)


def generate_alloc(statement, *, context):
    for argument in statement.arguments:
        arg = build_expression(argument)
        value_type = build_full_type(argument.value_type(
            declared_variables=context.variables,
        ).item_type)
        size = build_expression(statement.size)
        yield f"{arg} = new {value_type}[{size}];"


def generate_call(statement, *, context):
    function_name = statement.function(context).name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = {function_name}({parameters});"
    else:
        yield f"{function_name}({parameters});"
    if context.global_context.callbacks:
        yield r"""printf("return\n");"""


def generate_output(statement):
    format_string = ' '.join("%d" for _ in statement.arguments) + r'\n'
    args = ', '.join(build_expression(v) for v in statement.arguments)
    yield f'printf("{format_string}", {args});'


def generate_input(statement):
    format_string = ''.join("%d" for _ in statement.arguments)
    args = ', '.join("&" + build_expression(v) for v in statement.arguments)
    yield f'scanf("{format_string}", {args});'


def generate_if(statement, *, context):
    condition = build_expression(statement.condition)
    yield f"if( {condition} )" " {"
    yield from indent_all(generate_block(statement.then_body, context=context))
    yield "}"
    if statement.else_body is not None:
        yield "else {"
        yield from indent_all(generate_block(statement.else_body, context=context))
        yield "}"


def generate_for(statement, *, context):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for(int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
    body, body_context = statement.contextualized_body(context)
    yield from indent_all(generate_block(body, context=body_context))
    yield "}"


def build_callable_declarator(callable):
    signature = callable.signature
    return_type = build_full_type(signature.return_type)
    arguments = ', '.join(build_parameter(p) for p in signature.parameters)
    return f"{return_type} {callable.name}({arguments})"


def build_declaration(statement):
    type_specifier = build_type_specifier(statement.value_type)
    declarators = ', '.join(generate_declarators(statement))
    return f'{type_specifier} {declarators};'


def build_parameter(parameter):
    full_type = build_full_type(parameter.value_type)
    return f'{full_type} {parameter.name}'


def build_subscript(expression):
    array = build_expression(expression.array)
    index = build_expression(expression.index)
    return f"{array}[{index}]"


def build_expression(expression):
    builders = {
        "int_literal": lambda: f"{expression.value}",
        "reference": lambda: f"{expression.variable_name}",
        "subscript": lambda: build_subscript(expression),
    }
    return builders[expression.expression_type]()


def build_declarator(value_type, name):
    if value_type is None:
        return name
    builders = {
        "scalar": lambda: name,
        "array": lambda: "*" + build_declarator(value_type.item_type, name),
    }
    return builders[value_type.meta_type]()


def build_type_specifier(value_type):
    if value_type is None:
        return "void"
    builders = {
        "scalar": lambda: {
            int: "int",
        }[value_type.base_type],
        "array": lambda: build_type_specifier(value_type.item_type)
    }
    return builders[value_type.meta_type]()


def build_full_type(value_type):
    return build_type_specifier(value_type) + build_declarator(value_type, "")
