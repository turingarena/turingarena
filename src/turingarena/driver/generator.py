from abc import ABC, abstractmethod

from turingarena.util.visitor import Visitor


class CodeGen(ABC, Visitor):
    __slots__ = []

    def indent_all(self, lines):
        for line in lines:
            yield self.indent(line)

    def indent(self, line):
        if line is None:
            return None
        else:
            return "    " + line


class AbstractExpressionCodeGen(CodeGen):
    __slots__ = []

    def expression(self, e):
        return self.visit(e)

    def visit_SubscriptExpression(self, e):
        return f"{self.visit(e.array)}[{self.visit(e.index)}]"

    def visit_VariableReferenceExpression(self, e):
        return e.variable_name

    def visit_IntLiteralExpression(self, e):
        return str(e.value)


class InterfaceCodeGen(CodeGen):
    __slots__ = []

    def generate_to_file(self, interface, file):
        for line in self.generate(interface):
            if line is None:
                print("", file=file)
            else:
                print(line, file=file)

    def generate(self, interface):
        yield from self.generate_header(interface)
        yield from self.generate_constants_declarations(interface.constants)
        yield from self.generate_method_declarations(interface)
        yield from self.generate_main_block(interface)
        yield from self.generate_footer(interface)

    def generate_header(self, interface):
        yield from ()

    def generate_footer(self, interface):
        yield from ()

    def generate_method_declarations(self, interface):
        for func in interface.methods:
            yield from self.generate_method_declaration(func)

    def generate_constants_declarations(self, constants):
        if constants:
            yield self.line_comment("Constant declarations")
            for name, value in constants.items():
                yield from self.generate_constant_declaration(name, value)
            yield

    @abstractmethod
    def generate_method_declaration(self, method_declaration):
        pass

    @abstractmethod
    def generate_constant_declaration(self, name, value):
        pass

    @abstractmethod
    def generate_main_block(self, interface):
        pass

    @abstractmethod
    def line_comment(self, comment):
        pass


class StatementDescriptionCodeGen(AbstractExpressionCodeGen):
    def visit_IntermediateNode(self, n):
        pass

    def visit_ReadStatement(self, s):
        args = ", ".join(self.visit(a) for a in s.arguments)
        return f"read {args}"

    def visit_OutputStatement(self, s):
        args = ", ".join(self.visit(a) for a in s.arguments)
        return f"write {args}"

    def visit_CheckpointStatement(self, s):
        return f"checkpoint"

    def visit_CallStatement(self, s):
        method = s.method

        args = ", ".join(self.visit(p) for p in s.arguments)
        if method.has_return_value:
            return_value = f"{self.visit(s.return_value)} = "
        else:
            return_value = ""

        if method.has_callbacks:
            callbacks = " callbacks {...}"
        else:
            callbacks = ""

        return f"call {return_value}{method.name}({args}){callbacks}"

    def visit_ReturnStatement(self, s):
        return f"return {self.visit(s.value)}"

    def visit_ExitStatement(self, s):
        return "exit"

    def visit_BreakStatement(self, s):
        return "break"

    def visit_ForStatement(self, s):
        index = s.index
        return f"for {index.variable.name} to {self.visit(index.range)} " "{...}"

    def visit_LoopStatement(self, s):
        return "loop {...}"

    def visit_IfStatement(self, s):
        if s.else_body is not None:
            body = "{...} else {...}"
        else:
            body = "{...}"
        return f"if {self.visit(s.condition)} {body}"

    def visit_SwitchStatement(self, s):
        return f"switch {self.visit(s.value)} " "{...}"


class SkeletonCodeGen(InterfaceCodeGen, AbstractExpressionCodeGen):
    __slots__ = []

    @abstractmethod
    def visit_ReadStatement(self, s):
        pass

    @abstractmethod
    def visit_OutputStatement(self, s):
        pass

    @abstractmethod
    def visit_CallStatement(self, s):
        pass

    @abstractmethod
    def visit_IfStatement(self, s):
        pass

    @abstractmethod
    def visit_ForStatement(self, s):
        pass

    @abstractmethod
    def visit_LoopStatement(self, s):
        pass

    @abstractmethod
    def visit_SwitchStatement(self, s):
        pass

    @abstractmethod
    def visit_ExitStatement(self, statement):
        pass

    @abstractmethod
    def visit_ReturnStatement(self, statement):
        pass

    @abstractmethod
    def visit_BreakStatement(self, statement):
        pass

    def visit_IntermediateNode(self, s):
        # ignore any other node
        return []

    def visit_SequenceNode(self, node):
        for child in node.children:
            yield from self.generate_statement(child)

    @abstractmethod
    def visit_Allocation(self, allocation):
        pass

    def generate_main_block(self, interface):
        yield from self.visit(interface.main_block)

    def block(self, block):
        yield
        yield from self.indent_all(self.visit(block))

    def generate_statement(self, statement):
        if statement.comment is not None:
            yield self.line_comment(statement.comment)
        else:
            comment = StatementDescriptionCodeGen().visit(statement)
            if comment is not None:
                yield self.line_comment(comment)

        for var in statement.variables_to_declare:
            yield from self.generate_variable_declaration(var)

        for allocation in statement.allocations:
            yield from self.visit(allocation)

        if statement.needs_flush:
            yield from self.generate_flush()

        yield from self.visit(statement)

    @abstractmethod
    def generate_variable_declaration(self, declared_variable):
        pass

    @abstractmethod
    def generate_flush(self):
        pass


class TemplateCodeGen(InterfaceCodeGen):
    def generate_main_block(self, interface):
        yield from ()
