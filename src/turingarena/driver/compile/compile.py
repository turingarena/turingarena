import logging
from enum import Enum
from functools import partial

from turingarena.driver.common.analysis import InterfaceAnalyzer
from turingarena.driver.common.nodes import *
from turingarena.driver.common.variables import ReferenceDefinition, ReferenceResolution
from turingarena.driver.compile.analysis import CompileAnalyzer
from turingarena.driver.compile.diagnostics import *
from turingarena.driver.compile.parser import parse_interface
from turingarena.driver.compile.postprocess import CompilationPostprocessor
from turingarena.util.visitor import classvisitormethod

STATEMENT_CLASSES = {
    "checkpoint": Checkpoint,
    "read": Read,
    "write": Write,
    "call": Call,
    "return": Return,
    "exit": Exit,
    "for": For,
    "if": If,
    "loop": Loop,
    "break": Break,
    "switch": Switch,
}

SubscriptAst = namedtuple("SubscriptAst", ["expression_type", "array", "index"])
VariableAst = namedtuple("VariableAst", ["expression_type", "variable_name"])

EXPRESSION_CLASSES = {
    "int_literal": IntLiteral,
    "subscript": Subscript,
    "variable": Variable,
}


class ExpressionType(Enum):
    VALUE = 0
    REFERENCE = 1


class Compiler(CompileAnalyzer, InterfaceAnalyzer, CompilationPostprocessor):
    def compile_interface_source(self, source_text, descriptions=None):
        if descriptions is None:
            descriptions = {}

        ast = parse_interface(source_text)
        return self.transform(self.compile(Interface, ast))

    def error(self, e):
        if e not in self.diagnostics:
            self.diagnostics.append(e)

    def check(self, condition, e):
        if not condition:
            self.error(e)

    def compile(self, cls, ast):
        return self._on_compile(cls, ast)

    @classvisitormethod
    def _on_compile(self, cls, ast):
        pass

    def _on_compile_object(self, cls, ast):
        return cls()

    def _on_compile_Interface(self, cls, ast):
        compiler = self._replace(
            constants=(),
            methods=(),
        )

        for c in ast.constants_declarations:
            compiler = compiler.with_constant(
                compiler.compile(Constant, c)
            )

        for m in ast.method_declarations:
            compiler = compiler.with_method(
                compiler.compile(Prototype, m)
            )

        return cls(
            constants=compiler.constants,
            methods=compiler.methods,
            main=compiler._replace(
                prev_reference_actions=(),
                index_variables=(),
                in_loop=None,
            ).with_reference_actions(
                a(c.variable)
                for c in compiler.constants
                for a in [
                    partial(ReferenceDefinition, dimensions=0),
                    ReferenceResolution,
                ]
            ).compile(Block, ast.main),
        )

    def _on_compile_Constant(self, cls, ast):
        return cls(
            variable=Variable(name=ast.name),
            value=self.scalar(ast.value),
        )

    def _on_compile_Prototype(self, cls, ast):
        if self.in_callback:
            assert not ast.callbacks
            callbacks = ()
        else:
            callbacks = tuple(
                self._replace(in_callback=True).compile(Prototype, c)
                for c in ast.callbacks
            )

        return cls(
            name=ast.declarator.name,
            parameters=tuple(
                self.compile(Parameter, p)
                for p in ast.declarator.parameters
            ),
            has_return_value=(ast.declarator.type == 'function'),
            callbacks=callbacks,
        )

    def _on_compile_Parameter(self, cls, ast):
        dimensions = len(ast.indexes)
        if self.in_callback:
            self.check(dimensions == 0, CallbackParameterNotScalar(parameter=Snippet(ast)))
            dimensions = 0

        return cls(
            variable=Variable(name=ast.name),
            dimensions=dimensions,
        )

    def _on_compile_Read(self, cls, ast):
        arguments = []
        inner = self
        for a in ast.arguments:
            d = inner.reference_definition(a)
            arguments.append(d)
            inner = inner.with_reference_actions([ReferenceDefinition(d, dimensions=0)])
        return cls(arguments=tuple(arguments))

    def _on_compile_Write(self, cls, ast):
        return cls(arguments=[
            self.scalar_reference(a) for a in ast.arguments
        ])

    def _on_compile_Return(self, cls, ast):
        return cls(value=self.scalar(ast.value))

    def _on_compile_For(self, cls, ast):
        index = ForIndex(
            variable=Variable(name=ast.index),
            range=self.scalar(ast.range),
        )

        return cls(
            index=index,
            body=self.with_index_variable(index).with_reference_actions([
                ReferenceDefinition(index.variable, dimensions=0),
                ReferenceResolution(index.variable),
            ]).compile(Block, ast.body)
        )

    def _on_compile_Switch(self, cls, ast):
        value = self.scalar(ast.value)

        self.check(len(ast.cases) > 0, SwitchEmpty(switch=Location(ast)))

        cases = []
        labels = set()

        for case_ast in ast.cases:
            case = self.compile(Case, case_ast)
            cases.append(case)
            for l in case.labels:
                self.check(l not in labels, CaseLabelDuplicated(label=l))
                labels.add(l)

        return cls(
            value=value,
            cases=tuple(cases),
        )

    def _on_compile_Case(self, cls, ast):
        return cls(
            labels=[self.literal(l) for l in ast.labels],
            body=self.compile(Block, ast.body),
        )

    def _on_compile_If(self, cls, ast):
        return cls(
            condition=self.scalar(ast.condition),
            branches=IfBranches(
                then_body=self.compile(Block, ast.then_body),
                else_body=self.compile(Block, ast.else_body) if ast.else_body is not None else None,
            ),
        )

    def _on_compile_Loop(self, cls, ast):
        return cls(
            body=self.with_loop().compile(Block, ast.body)
        )

    def _on_compile_Break(self, cls, ast):
        self.check(self.in_loop, BreakOutsideLoop(statement=Snippet(ast)))
        return cls()

    def _on_compile_Call(self, cls, ast):
        method = self.methods_by_name.get(ast.name)

        if method is None:
            self.error(MethodNotDeclared(name=ast.name))
            method = Prototype(
                name=ast.name,
                parameters=(),
                has_return_value=False,
                callbacks=(),
            )
        else:
            if method.has_return_value:
                self.check(ast.return_value is not None, IgnoredReturnValue(name=method.name))
            else:
                self.check(ast.return_value is None, NoReturnValue(name=method.name))

        self.check(len(ast.arguments) == len(method.parameters), InvalidNumberOfArguments(
            name=method.name,
            n_parameters=len(method.parameters),
            n_arguments=len(ast.arguments),
        ))

        arguments = []

        for parameter_declaration, argument_ast in zip(method.parameters, ast.arguments):
            argument = self.value(argument_ast)
            argument_dimensions = self.dimensions(argument)
            self.check(argument_dimensions == parameter_declaration.dimensions, InvalidArgument(
                name=method.name,
                parameter=parameter_declaration.variable.name,
                dimensions=parameter_declaration.dimensions,
                argument=Snippet(argument_ast),
                argument_dimensions=argument_dimensions,
            ))
            arguments.append(argument)

        callback_prototypes_by_name = {c.name: c for c in method.callbacks}
        body_by_name = {}
        for cb in ast.callbacks:
            prototype = self._replace(in_callback=True).compile(Prototype, cb)
            name = prototype.name
            self.check(
                name in callback_prototypes_by_name,
                CallbackNotDeclared(name=method.name, callback=name),
            )
            self.check(name not in body_by_name, CallbackAlreadyImplemented(name=name))
            self.check(
                prototype == callback_prototypes_by_name[name],
                CallbackPrototypeMismatch(name=name),
            )
            body_by_name[name] = cb.body

        callbacks = [
            self.callback_implementation(
                prototype=prototype,
                index=index,
                ast=body_by_name.get(prototype.name),
            )
            for index, prototype in enumerate(method.callbacks)

        ]

        if ast.return_value is not None:
            return_value = self.reference_definition(ast.return_value)
        else:
            return_value = None

        return cls(
            method=method,
            arguments=tuple(arguments),
            return_value=return_value,
            callbacks=tuple(callbacks),
        )

    def callback_implementation(self, prototype, index, ast):
        if ast is None:
            nodes = []
            if prototype.parameters:
                nodes.append(Write(tuple(p.variable for p in prototype.parameters)))
            if prototype.has_return_value:
                return_var = Variable("ans")
                nodes.append(Read([return_var]))
                nodes.append(Return(return_var))

            body = Block(tuple(nodes))
        else:
            body = self.with_reference_actions([
                ReferenceDefinition(p.variable, dimensions=0)
                for p in prototype.parameters
            ]).compile(Block, ast)

        return Callback(
            index=index,
            prototype=prototype,
            body=body
        )

    def _on_compile_Block(self, cls, ast):
        return cls(tuple(self.statements(ast.statements)))

    def statements(self, asts):
        inner = self
        for ast in asts:
            node = inner.compile(STATEMENT_CLASSES[ast.statement_type], ast)
            yield node
            inner = inner.with_reference_actions(inner.reference_actions(node))

    def scalar_reference(self, ast):
        assert self.expression_type is None
        e = self._replace(expression_type=ExpressionType.REFERENCE).expression(ast)
        self.check(self.is_defined(e), ReferenceNotDefined(expression=Snippet(ast)))
        return self.check_scalar(ast, e)

    def reference_definition(self, ast):
        assert self.expression_type is None
        e = self._replace(expression_type=ExpressionType.REFERENCE).expression(ast)
        self.check(not self.is_defined(e), ReferenceAlreadyDefined(expression=Snippet(ast)))
        return e

    def value(self, ast):
        assert self.expression_type is None
        e = self._replace(expression_type=ExpressionType.VALUE).expression(ast)
        # FIXME: should give a more precise error
        self.check(self.is_defined(e), ReferenceNotDefined(expression=Snippet(ast)))
        return e

    def scalar(self, ast):
        return self.check_scalar(ast, self.value(ast))

    def check_scalar(self, ast, e):
        if self.dimensions(e) > 0:
            self.error(ExpressionNotScalar(expression=Snippet(ast)))
        return e

    def literal(self, ast):
        e = self.value(ast)
        if not isinstance(e, IntLiteral):
            self.error(ExpressionNotLiteral(expression=Snippet(ast)))
        return e

    def expression(self, ast):
        assert self.expression_type is not None
        ast = self._preprocess_expression_ast(ast)
        return self._on_compile(EXPRESSION_CLASSES[ast.expression_type], ast)

    def _preprocess_expression_ast(self, ast):
        if ast.expression_type == "reference_subscript":
            new_ast = VariableAst("variable", ast.variable_name)
            for i in ast.indices:
                new_ast = SubscriptAst("subscript", new_ast, i)
            ast = new_ast
        return ast

    def _on_compile_IntLiteral(self, cls, ast):
        self.check(
            self.expression_type is ExpressionType.VALUE,
            InvalidReference(expression=Snippet(ast)),
        )

        return cls(value=int(ast.int_literal))

    def _on_compile_Variable(self, cls, ast):
        return cls(ast.variable_name)

    def _on_compile_Subscript(self, cls, ast):
        array = self._replace(
            index_variables=self.index_variables[:-1],
        ).expression(ast.array)

        index = self._replace(
            expression_type=None,
        ).value(ast.index)

        if self.expression_type is ExpressionType.REFERENCE:
            if not self.index_variables:
                self.error(UnexpectedIndexForReference(expression=Snippet(ast.index)))
            else:
                self.check(
                    index == self.index_variables[-1].variable,
                    InvalidIndexForReference(
                        index=self.index_variables[-1].variable.name,
                        expression=Snippet(ast.index),
                    ),
                )

        return cls(array, index)


def compile_interface(source_text):
    compiler = Compiler.create()
    interface = compiler.compile_interface_source(source_text)

    for msg in compiler.diagnostics:
        logging.warning(f"interface contains an error: {msg}")

    return interface


def load_interface(path):
    with open(path) as f:
        return compile_interface(f.read())
