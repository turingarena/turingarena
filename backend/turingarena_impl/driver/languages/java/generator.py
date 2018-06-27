from turingarena_impl.driver.generator import InterfaceCodeGen, SkeletonCodeGen, TemplateCodeGen

class JavaCodeGen(InterfaceCodeGen):

    def build_parameter(self, parameter):
        arrays = "[]" * parameter.dimensions
        return f"int {parameter.name}{arrays}"

    def build_signature(self, callable, callbacks):
        return_type = "int" if callable.has_return_value else "void"
        value_parameters = [self.build_parameter(p) for p in callable.parameters]
        # TODO
        #callback_parameters = [
        #    self.build_signature(callback, [])
        #    for callback in callbacks
        #]
        #parameters = ", ".join(value_parameters + callback_parameters)
        parameters = ", ".join(value_parameters)
        return f"{return_type} {callable.name}({parameters})"

    def build_method_signature(self, func):
        return self.build_signature(func, func.callbacks)

    def line_comment(self, comment):
        return f"// {comment}"

    def generate_footer(self, interface):
        return "}"



class JavaSkeletonCodeGen(JavaCodeGen, SkeletonCodeGen):
    def generate_header(self, interface):
        yield 'import java.util.Scanner;'
        yield
        yield 'abstract class Skeleton {'
        yield self.indent('private static final Scanner in = new Scanner(System.in);')

    def generate_variable_declaration(self, declared_variable):
        yield f'int{"[]" * declared_variable.dimensions} {declared_variable.name};'

    #def generate_variable_allocation(self, allocated_variable):
    #    var = allocated_variable.name
    #    for index in allocated_variable.indexes:
    #        var += f'[{index}]'
    #    size = self.expression(allocated_variable.size)
    #    yield f'{var} = new int{"[]" * allocated_variable.dimensions}[{size}];'

    def generate_variable_allocation(self, variable, indexes, size):
        indexes = "".join(f"[{idx.variable.name}]" for idx in indexes)
        dimensions = "[]" * (variable.dimensions - len(indexes) - 1)
        size = self.expression(size)
        yield f"{variable.name}{indexes} = new int[{size}]{dimensions};"

    def generate_method_declaration(self, method_declaration):
        yield self.indent(f'abstract {self.build_method_signature(method_declaration)};')

    def generate_main_block(self, interface):
        yield
        yield 'public static void main(String args[]) {'
        yield self.indent('Solution __solution = new Solution();')
        yield from self.block(interface.main_block)
        yield '}'

    def generate_callback(self, callback):
        # TODO
        pass

    def call_statement_body(self, call_statement):

        method = call_statement.method

        # TODO
        #for callback in call_statement.callbacks:
        #    yield from self.generate_callback(callback)

        value_arguments = [self.expression(p) for p in call_statement.arguments]

        # TODO
        #callback_arguments = [
        #    f"_callback_{callback_signature.name}"
        #    for callback_signature in method.callbacks
        #]

        # TODO
        #parameters = ", ".join(value_arguments + callback_arguments)
        parameters = ", ".join(value_arguments)

        if method.has_return_value:
            return_value = f"{self.expression(call_statement.return_value)} = "
        else:
            return_value = ""

        yield f"{return_value}__solution.{method.name}({parameters});"

    def call_statement(self, call_statement):
        if call_statement.method.has_callbacks:
            # TODO
            pass
            #yield "{"
            #yield from self.indent_all(self.call_statement_body(call_statement))
            #yield "}"
        else:
            yield from self.call_statement_body(call_statement)

    # TODO
    #def callback_statement(self, statement):
    #    callback = statement.callback
    #    yield f'{self.build_method_signature(callback)}'' {'
    #    yield from self.block(statement.callback.synthetic_body)
    #    yield '}'
    #    yield

    def write_statement(self, statement):
        format_string = ' '.join('%d' for _ in statement.arguments) + r'\n'
        args = ', '.join(self.expression(v) for v in statement.arguments)
        yield f'System.out.printf("{format_string}", {args});'

    def read_statement(self, statement):
        for arg in statement.arguments:
            yield f'{self.expression(arg)} = in.nextInt();'

    def if_statement(self, statement):
        condition = self.expression(statement.condition)
        yield f'if ({condition})'' {'
        yield from self.block(statement.then_body)
        if statement.else_body is not None:
            yield '} else {'
            yield from self.block(statement.else_body)
        yield '}'

    def for_statement(self, statement):
        index_name = statement.index.variable.name
        size = self.expression(statement.index.range)
        yield f'for (int {index_name} = 0; {index_name} < {size}; {index_name}++)'' {'
        yield from self.block(statement.body)
        yield '}'

    def loop_statement(self, loop_statement):
        yield 'while (true) {'
        yield from self.block(loop_statement.body)
        yield '}'

    def build_switch_cases(self, variable, labels):
        variable = self.expression(variable)
        return ' || '.join(f'{variable} == {label}' for label in labels)

    def switch_statement(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        yield f'if ({self.build_switch_condition(switch_statement.variable, cases[0].labels)})'' {'
        yield from self.block(cases[0].body)
        for case in cases[1:]:
            yield '}' f' else if ({self.build_switch_condition(switch_statement.variable, case.labels)}) ' '{'
            yield from self.block(case.body)
        yield '}'

    def generate_flush(self):
        yield 'System.out.flush();'

    def checkpoint_statement(self, checkpoint_statement):
        yield 'System.out.println(0);'

    def exit_statement(self, exit_statement):
        yield 'System.exit(0);'

    def return_statement(self, return_statement):
        yield f'return {self.expression(return_statement.value)};'

    def break_statement(self, break_statement):
        yield 'break;'


class JavaTemplateCodeGen(JavaCodeGen, TemplateCodeGen):
    def generate_header(self, interface):
        yield 'class Solution extends Skeleton {'

    def generate_method_declaration(self, method_declaration):
        yield
        yield self.indent(f"{self.build_method_signature(method_declaration)}" " {")
        yield self.indent(self.indent('// TODO'))
        yield self.indent('}')
