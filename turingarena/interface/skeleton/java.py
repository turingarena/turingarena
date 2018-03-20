from turingarena.common import indent_all, indent


def generate_skeleton_java(interface):
    yield "import java.util.Scanner;"
    yield
    yield "abstract class Skeleton {"
    yield indent("private static final Scanner in = new Scanner(System.in);")
    for statement in interface.body.statements:
        yield
        yield from indent_all(generate_skeleton_statement(statement, interface=interface))
    yield "}"
    yield


def generate_template_java(interface):
    yield "class Solution extends Skeleton {"
    for statement in interface.body.statements:
        yield from indent_all(generate_template_statement(statement, interface=interface))
    yield "}"


def generate_skeleton_statement(statement, *, interface):
    generators = {
        "var": lambda: ["final " + build_declaration(statement)],
        "function": lambda: generate_function(statement),
        "callback": lambda: generate_callback(statement, interface=interface),
        "main": lambda: generate_main(statement, interface=interface),
        "init": lambda: generate_constructor(statement, interface=interface),
    }
    return generators[statement.statement_type]()


def generate_template_statement(statement, *, interface):
    generators = {
        "var": lambda: ["// global " + build_declaration(statement)],
        "function": lambda: generate_function_template(statement),
        "callback": lambda: [],
        "main": lambda: [],
        "init": lambda: [],
    }
    return generators[statement.statement_type]()


def generate_function(statement):
    yield f"abstract {build_callable_declarator(statement.function)};"


def generate_function_template(statement):
    yield
    yield f"{build_callable_declarator(statement.function)}" " {"
    yield indent("// TODO")
    if statement.function.signature.return_type:
        yield indent("return 0;")
    yield "}"


def generate_callback(statement, *, interface):
    callback = statement.callback
    yield f"{build_callable_declarator(callback)}" " {"
    yield indent(rf"""System.out.println("{callback.name}");""")
    yield from indent_all(generate_block(callback.body, interface=interface))
    yield "}"


def generate_callback_template(statement, *, interface):
    callback = statement.callback
    yield f"{build_callable_declarator(callback)};"


def generate_main(statement, *, interface):
    yield "void _run() {"
    yield from indent_all(generate_block(statement.main.body, interface=interface))
    yield "}"
    yield
    yield "public static void main(String args[]) {"
    yield indent("new Solution()._run();")
    yield "}"


def generate_constructor(statement, *, interface):
    yield "Skeleton() {"
    yield from indent_all(generate_block(statement.init.body, interface=interface))
    yield "}"


def generate_block(block, *, interface):
    for statement in block.statements:
        yield from generate_block_statement(statement, interface=interface)


def generate_block_statement(statement, *, interface):
    generators = {
        "var": lambda: [build_declaration(statement)],
        "alloc": lambda: generate_alloc(statement),
        "input": lambda: generate_input(statement),
        "output": lambda: generate_output(statement),
        "flush": lambda: ["System.out.flush();"],
        "call": lambda: generate_call(statement, interface=interface,),
        "for": lambda: generate_for(statement, interface=interface),
        "if": lambda: generate_if(statement, interface=interface),
        "exit": lambda: ["System.exit(0);"],
        "return": lambda: [f"return {build_expression(statement.value)};"],
    }
    return generators[statement.statement_type]()


def generate_alloc(statement):
    size = build_expression(statement.size)
    for argument in statement.arguments:
        arg = build_expression(argument)
        yield f"{arg} = new {build_alloc_type(argument.value_type.item_type, size)};"


def build_alloc_type(var_type, size):
    if var_type.meta_type == "array":
        return build_alloc_type(var_type.item_type, size) + "[]"
    else:
        return {
            int: "int",
        }[var_type.base_type] + f"[{size}]"


def generate_call(statement, *, interface):
    function_name = statement.function.name
    parameters = ", ".join(build_expression(p) for p in statement.parameters)
    if statement.return_value is not None:
        return_value = build_expression(statement.return_value)
        yield f"{return_value} = {function_name}({parameters});"
    else:
        yield f"{function_name}({parameters});"
    if interface.signature.callbacks:
        yield 'System.out.println("return");'


def generate_output(statement):
    format_string = ' '.join(build_format(v) for v in statement.arguments) + r'\n'
    args = ', '.join(build_expression(v) for v in statement.arguments)
    yield f'System.out.printf("{format_string}", {args});'


def generate_input(statement):
    for arg in statement.arguments:
        yield f"{build_expression(arg)} = " + {
            int: "in.nextInt()",
        }[arg.value_type.base_type] + ";"


def generate_if(statement, *, interface):
    condition = build_expression(statement.condition)
    yield f"if ({condition})" " {"
    yield from indent_all(generate_block(statement.then_body, interface=interface))
    if statement.else_body is not None:
        yield "} else {"
        yield from indent_all(generate_block(statement.else_body, interface=interface))
    yield "}"


def generate_for(statement, *, interface):
    index_name = statement.index.variable.name
    size = build_expression(statement.index.range)
    yield f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
    yield from indent_all(generate_block(statement.body, interface=interface))
    yield "}"


def build_callable_declarator(callable):
    signature = callable.signature
    return_type = build_type(signature.return_type)
    arguments = ', '.join(build_parameter(p) for p in signature.parameters)
    return f"{return_type} {callable.name}({arguments})"


def build_declaration(statement):
    type = build_type(statement.value_type)
    declarators = ', '.join(v.name for v in statement.variables)
    return f'{type} {declarators};'


def build_parameter(parameter):
    value_type = build_type(parameter.value_type)
    return f'{value_type} {parameter.name}'


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


def build_type(value_type):
    if value_type is None:
        return "void"
    builders = {
        "scalar": lambda: {
            int: "int",
        }[value_type.base_type],
        "array": lambda: f"{build_type(value_type.item_type)}[]"
    }
    return builders[value_type.meta_type]()


def build_format(expr):
    return {
        int: "%d",
    }[expr.value_type.base_type]
