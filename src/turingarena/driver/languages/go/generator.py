from turingarena.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen


class GoCodeGen(InterfaceCodeGen):
    def build_parameter(self, parameter):
        indirections = "[]" * parameter.dimensions
        return f"{parameter.name} {indirections}int"

    def build_signature(self, callable, callbacks, param=False):
        return_type = " int" if callable.has_return_value else ""
        value_parameters = [self.build_parameter(p) for p in callable.parameters]
        callback_parameters = [
            self.build_signature(callback, [], param=True)
            for callback in callbacks
        ]
        parameters = ", ".join(value_parameters + callback_parameters)
        if param:
            return f"{callable.name} func({parameters}){return_type}"
        else:
            return f"func {callable.name}({parameters}){return_type}"

    def build_method_signature(self, func):
        return self.build_signature(func, func.callbacks)

    def line_comment(self, comment):
        return f"// {comment}"


class GoSkeletonCodeGen(GoCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        yield "package main"
        yield
        yield 'import "fmt"'
        yield 'import "os"'
        yield

    def generate_variable_declaration(self, declared_variable):
        yield f"var {declared_variable.name} {'[]' * declared_variable.dimensions + 'int'}"

    def generate_method_declaration(self, method_declaration):
        return []

    def generate_constant_declaration(self, name, value):
        return []

    def generate_variable_allocation(self, variable, indexes, size):
        idx = "".join(f"[{idx.variable.name}]" for idx in indexes)
        dimensions = "[]" * (variable.dimensions - len(indexes))
        size = self.expression(size)
        yield f"{variable.name}{idx} = make({dimensions}int, {size})"

    def generate_main_block(self, interface):
        yield "func main() {"
        yield from self.block(interface.main_block)
        yield "}"

    def generate_callback(self, callback):
        params = ", ".join(f"{parameter.name}" for parameter in callback.parameters) + " int"
        if callback.has_return_value:
            return_value = "int"
        else:
            return_value = ""

        yield f"_callback_{callback.name} := func({params}) {return_value}" " {"
        yield from self.block(callback.synthetic_body)
        yield "}"

    def call_statement_body(self, call_statement):
        method = call_statement.method

        for callback in call_statement.callbacks:
            yield from self.generate_callback(callback)

        value_arguments = [self.expression(p) for p in call_statement.arguments]
        callback_arguments = [
            f"_callback_{callback_signature.name}"
            for callback_signature in method.callbacks
        ]
        parameters = ", ".join(value_arguments + callback_arguments)
        if method.has_return_value:
            return_value = f"{self.expression(call_statement.return_value)} = "
        else:
            return_value = ""

        yield f"{return_value}{method.name}({parameters});"

    def call_statement(self, call_statement):
        if call_statement.method.has_callbacks:
            yield "{"
            yield from self.indent_all(self.call_statement_body(call_statement))
            yield "}"
        else:
            yield from self.call_statement_body(call_statement)

    def write_statement(self, write_statement):
        format_string = " ".join("%d" for _ in write_statement.arguments) + r"\n"
        args = ", ".join(self.expression(v) for v in write_statement.arguments)
        yield f'fmt.Printf("{format_string}", {args})'

    def read_statement(self, statement):
        format_string = "".join("%d" for _ in statement.arguments)
        scanf_args = ", ".join("&" + self.expression(v) for v in statement.arguments)
        yield f'fmt.Scanf("{format_string}", {scanf_args});'

    def if_statement(self, statement):
        condition = self.expression(statement.condition)
        yield f"if {condition}" " {"
        yield from self.block(statement.then_body)
        if statement.else_body:
            yield "} else {"
            yield from self.block(statement.else_body)
        yield "}"

    def for_statement(self, s):
        index_name = s.index.variable.name
        size = self.expression(s.index.range)
        yield f"for {index_name} := 0; {index_name} < {size}; {index_name}++" " {"
        yield from self.block(s.body)
        yield "}"

    def loop_statement(self, statement):
        yield "for {"
        yield from self.block(statement.body)
        yield "}"

    def build_switch_condition(self, variable, labels):
        variable = self.expression(variable)
        return " || ".join(f"{variable} == {label}" for label in labels)

    def switch_statement(self, statement):
        yield "switch {"
        for case in statement.cases:
            yield f"case {self.build_switch_condition(statement.variable, case.labels)}:"
            yield from self.block(case.body)
        yield "}"

    def exit_statement(self, statement):
        yield "os.Exit(0)"

    def return_statement(self, statement):
        yield f"return {self.expression(statement.value)};"

    def break_statement(self, statement):
        yield "break"

    def generate_flush(self):
        yield "os.Stdout.Sync()"


class GoTemplateCodeGen(GoCodeGen, TemplateCodeGen):
    def generate_constant_declaration(self, name, value):
        yield f"const {name} = {value}"

    def generate_method_declaration(self, method_declaration):
        yield
        yield f"{self.build_method_signature(method_declaration)}" " {"
        yield self.indent("// TODO")
        yield "}"
