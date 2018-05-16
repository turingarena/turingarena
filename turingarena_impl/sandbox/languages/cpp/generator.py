from turingarena_impl.sandbox.languages.generator import CodeGen


class CppCodeGen(CodeGen):
    @staticmethod
    def build_callback_signature(parameter):
        return_type = "int" if parameter.has_return_value else "void"
        parameters = ", ".join([f"int {a}" for a in parameter.parameters])
        return f"{return_type} {parameter.name}({parameters})"

    @classmethod
    def build_parameter(cls, parameter):
        if parameter.value_type.meta_type == "callback":
            return cls.build_callback_signature(parameter)
        else:
            indirections = "*" * parameter.value_type.dimensions if parameter.value_type.meta_type == "array" else ""
            return f"int {indirections}{parameter.name}"

    @classmethod
    def build_function_signature(cls, func):
        return_type = "int" if func.has_return_value else "void"
        parameters = ", ".join(cls.build_parameter(p) for p in func.parameters)
        if func.has_callbacks:
            callbacks = ", ".join(
                cls.build_callback_signature(callback)
                for callback in func.callbacks_signature
            )
        else:
            callbacks = ""
        if len(parameters) > 0 and len(callbacks) > 0:
            parameters += ", "
        return f"{return_type} {func.name}({parameters}{callbacks})"


class CppSkeletonCodeGen(CppCodeGen):
    def generate_header(self):
        yield "#include <cstdio>"
        yield "#include <cstdlib>"
        yield "#include <cassert>"
        yield

    def generate_variable_declaration(self, declared_variable):
        pointers = "*" * declared_variable.dimensions
        yield f"static int {pointers}{declared_variable.name};"

    def generate_variable_allocation(self, allocated_variable):
        indexes = ""
        for idx in allocated_variable.indexes:
            indexes += f"[{idx}]"
        dimensions = "*" * allocated_variable.dimensions
        yield f"{allocated_variable.name}{indexes} = new int{dimensions}[{allocated_variable.size}];"

    def generate_function_declaration(self, s):
        yield f"{self.build_function_signature(s)};"

    def generate_main_block(self):
        yield
        yield "int main() {"
        yield from self.block_content(self.interface.main)
        yield "}"

    def generate_callback(self, callback, index):
        params = ", ".join(f"int {parameter.name}" for parameter in callback.parameters)
        if callback.has_return_value:
            return_value = " -> int"
        else:
            return_value = ""

        yield f"auto _callback_{callback.name} = []({params}){return_value}" " {"
        yield self.indent(fr"""printf("%d\n", {index});""")
        yield from self.block_content(callback.body)
        yield "};"

    def call_statement_body(self, call_statement):
        function_name = call_statement.function.name
        func = call_statement.function

        for callback_signature in func.callbacks_signature:
            yield from self.generate_callback(*self.find_callback(callback_signature, call_statement))

        value_arguments = [self.expression(p) for p in call_statement.parameters]
        callback_arguments = [
            f"_callback_{callback_signature.name}"
            for callback_signature in func.callbacks_signature
        ]
        parameters = ", ".join(value_arguments + callback_arguments)
        if func.has_return_value:
            return_value = f"{self.expression(call_statement.return_value)} = "
        else:
            return_value = ""

        yield f"{return_value}{function_name}({parameters});"

    def call_statement(self, call_statement):
        if call_statement.has_callbacks:
            yield "{"
            yield from self.indent_all(self.call_statement_body(call_statement))
            yield "}"
        else:
            yield from self.call_statement_body(call_statement)

    def write_statement(self, write_statement):
        format_string = " ".join("%d" for _ in write_statement.arguments) + r"\n"
        args = ", ".join(self.expression(v) for v in write_statement.arguments)
        yield f"""printf("{format_string}", {args});"""

    def read_statement(self, statement):
        format_string = "".join("%d" for _ in statement.arguments)
        scanf_args = ", ".join("&" + self.expression(v) for v in statement.arguments)
        scanf_call = f"""scanf("{format_string}", {scanf_args})"""
        error_message = '"unable to read input"'
        yield f"assert({scanf_call} == {len(statement.arguments)} && {error_message});"

    def if_statement(self, statement):
        condition = self.expression(statement.condition)
        yield f"if ({condition})" " {"
        yield from self.block_content(statement.then_body)
        if statement.else_body:
            yield "} else {"
            yield from self.block_content(statement.else_body)
        yield "}"

    def for_statement(self, s):
        index_name = s.index.variable.name
        size = self.expression(s.index.range)
        yield f"for (int {index_name} = 0; {index_name} < {size}; {index_name}++)" " {"
        yield from self.block_content(s.body)
        yield "}"

    def loop_statement(self, statement):
        yield "while (true) {"
        yield from self.block_content(statement.body)
        yield "}"

    def build_switch_condition(self, variable, labels):
        variable = self.expression(variable)
        return " || ".join(f"{variable} == {label}" for label in labels)

    def switch_statement(self, statement):
        cases = [case for case in statement.cases]
        yield f"if ({self.build_switch_condition(statement.variable, cases[0].labels)}) " "{"
        yield from self.block_content(cases[0].body)
        for case in cases[1:]:
            yield "}" f" else if ({self.build_switch_condition(statement.variable, case.labels)}) " "{"
            yield from self.block_content(case.body)
        yield "}"

    def checkpoint_statement(self, statement):
        yield r"""printf("%d\n", 0);"""

    def exit_statement(self, statement):
        yield "exit(0);"

    def return_statement(self, statement):
        yield f"return {self.expression(statement.value)};"

    def break_statement(self, statement):
        yield "break;"

    def generate_flush(self):
        yield "fflush(stdout);"


class CppTemplateCodeGen(CppCodeGen):
    def generate_function_declaration(self, func):
        yield
        yield f"{self.build_function_signature(func)}" " {"
        yield self.indent("// TODO")
        yield "}"

    def generate_main_block(self):
        yield from ()
