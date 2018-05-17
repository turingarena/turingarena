from turingarena_impl.sandbox.languages.generator import CodeGen

class JavaCodeGen(CodeGen):
    @classmethod
    def build_callable_declarator(cls, callable):
        return_type = cls.build_type(callable.return_type)
        parameters = ', '.join(cls.build_parameter(p) for p in callable.parameters)
        return f"{return_type} {callable.name}({parameters})"

    @classmethod
    def build_parameter(cls, parameter):
        value_type = cls.build_type(parameter.value_type)
        return f'{value_type} {parameter.name}'

    @classmethod
    def build_type(cls, value_type):
        if value_type is None:
            return "void"
        builders = {
            "scalar": lambda: {
                int: "int",
            }[value_type.base_type],
            "array": lambda: f"{cls.build_type(value_type.item_type)}[]"
        }
        return builders[value_type.meta_type]()

    def generate_footer(self):
        yield "}"


class JavaSkeletonCodeGen(JavaCodeGen):
    def generate_header(self):
        yield 'import java.util.Scanner;'
        yield
        yield 'abstract class Skeleton {'
        yield self.indent('private static final Scanner in = new Scanner(System.in);')

    def generate_function_declaration(self, function):
        yield f'abstract {self.build_callable_declarator(function)};'

    def callback_statement(self, statement):
        callback = statement.callback
        yield f'{self.build_callable_declarator(callback)}'' {'
        yield from self.block_content(statement.callback.synthetic_body)
        yield '}'
        yield

    def main_statement(self, statement):
        yield
        yield 'public static void main(String args[]) {'
        yield self.indent('Solution __solution = new Solution();')
        yield from self.block_content(statement.body)
        yield '}'

    def generate_variable_allocation(self, allocated_variable):
        var = allocated_variable.name
        for index in allocated_variable.indexes:
            var += f'[{index}]'
        size = self.expression(allocated_variable.size)
        yield f'{var} = new int{"[]" * allocated_variable.dimensions}[{size}];'

    def generate_variable_declaration(self, declared_variable):
        yield f'int{"[]" * declared_variable.dimensions} {declared_variable.name}'

    def call_statement(self, statement):
        function_name = statement.function_name
        parameters = ', '.join(self.expression(p) for p in statement.parameters)
        if statement.return_value is not None:
            return_value = self.expression(statement.return_value)
            yield f'{return_value} = __solution.{function_name}({parameters});'
        else:
            yield f'__solution.{function_name}({parameters});'

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
        yield from self.block_content(statement.then_body)
        if statement.else_body is not None:
            yield '} else {'
            yield from self.block_content(statement.else_body)
        yield '}'

    def for_statement(self, statement):
        index_name = statement.index.variable.name
        size = self.expression(statement.index.range)
        yield f'for (int {index_name} = 0; {index_name} < {size}; {index_name}++)'' {'
        yield from self.block_content(statement.body)
        yield '}'

    def loop_statement(self, loop_statement):
        yield 'while (true) {'
        yield from self.block_content(loop_statement.body)
        yield '}'

    def build_switch_cases(self, variable, labels):
        variable = self.expression(variable)
        return ' || '.join(f'{variable} == {label}' for label in labels)

    def switch_statement(self, switch_statement):
        cases = [case for case in switch_statement.cases]
        yield f'if ({self.build_switch_condition(switch_statement.variable, cases[0].labels)})'' {'
        yield from self.block_content(cases[0].body)
        for case in cases[1:]:
            yield '}' f' else if ({self.build_switch_condition(switch_statement.variable, case.labels)}) ' '{'
            yield from self.block_content(case.body)
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


class JavaTemplateCodeGen(JavaCodeGen):
    def generate_header(self):
        yield 'class Solution extends Skeleton {'

    def generate_function_declaration(self, statement):
        yield
        yield f'{self.build_callable_declarator(statement.function)}'' {'
        yield self.indent('// TODO')
        yield '}'

    def generate_main_block(self):
        yield from ()
