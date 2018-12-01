import itertools
import logging
from collections import namedtuple
from enum import Enum
from functools import partial

from turingarena.driver.interface.analysis import TreeAnalyzer
from turingarena.driver.interface.diagnostics import SwitchEmpty, Location, ExpressionNotScalar, Snippet, \
    ExpressionNotLiteral, CaseLabelDuplicated, InvalidReference, ReferenceAlreadyDefined, MethodNotDeclared, \
    IgnoredReturnValue, NoReturnValue, CallbackAlreadyImplemented, CallbackNotDeclared, InvalidNumberOfArguments, \
    InvalidArgument, ReferenceNotDefined, InvalidIndexForReference, InvalidSubscript, BreakOutsideLoop, \
    UnexpectedIndexForReference, CallbackParameterNotScalar
from turingarena.driver.interface.interface import Interface
from turingarena.driver.interface.nodes import CallbackStart, CallbackEnd, \
    ForIndex, Case, CallbackImplementation, ParameterDeclaration, \
    ConstantDeclaration, Block, Variable, Write, Read, Return, IntLiteral, \
    Subscript, Checkpoint, Call, Exit, For, If, Loop, Break, Switch, Prototype
from turingarena.driver.interface.parser import parse_interface
from turingarena.driver.interface.variables import ReferenceDefinition, ReferenceResolution
from turingarena.util.visitor import visitormethod, classvisitormethod


def compile_interface(source_text, descriptions=None):
    # FIXME: descriptions

    compiler = Compiler.create()
    interface = compiler.compile(source_text)

    for msg in compiler.diagnostics:
        logging.warning(f"interface contains an error: {msg}")

    return interface


def load_interface(path):
    with open(path) as f:
        return compile_interface(f.read())


class ExpressionType(Enum):
    VALUE = 0
    REFERENCE = 1


SubscriptAst = namedtuple("SubscriptAst", ["expression_type", "array", "index"])
VariableAst = namedtuple("VariableAst", ["expression_type", "variable_name"])


class Compiler(namedtuple("Compiler", [
    "constants",
    "methods",
    "prev_reference_actions",
    "index_variables",
    "in_loop",
    "diagnostics",
    "expression_type",
]), TreeAnalyzer):
    @classmethod
    def create(cls):
        return cls(
            constants=None,
            methods=None,
            prev_reference_actions=None,
            index_variables=None,
            in_loop=None,
            diagnostics=[],
            expression_type=None,
        )

    def compile(self, source_text, descriptions=None):
        if descriptions is None:
            descriptions = {}

        ast = parse_interface(source_text)
        return self.interface(ast)

    def error(self, e):
        if e not in self.diagnostics:
            self.diagnostics.append(e)

    def check(self, condition, e):
        if not condition:
            self.error(e)

    def with_constant(self, declaration):
        return self._replace(constants=self.constants + (declaration,))

    def with_method(self, method):
        return self._replace(methods=self.methods + (method,))

    def interface(self, ast):
        compiler = self._replace(
            constants=(),
            methods=(),
        )

        for c in ast.constants_declarations:
            compiler = compiler.with_constant(
                compiler.constant_declaration(c)
            )

        for m in ast.method_declarations:
            compiler = compiler.with_method(
                compiler.method(m)
            )

        return Interface(
            constants=compiler.constants,
            methods=compiler.methods,
            main_block=compiler._replace(
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
            ).block(
                ast.main_block,
                prepend_nodes=[Checkpoint()],
                append_nodes=[Exit()],
            ),
        )

    @property
    def methods_by_name(self):
        return {m.name: m for m in self.methods}

    def constant_declaration(self, ast):
        return ConstantDeclaration(
            variable=Variable(name=ast.name),
            value=self.scalar(ast.value),
        )

    def method(self, ast):
        return self.prototype(ast, is_callback=False)

    def callback(self, ast):
        return self.prototype(ast, is_callback=True)

    def prototype(self, ast, is_callback):
        if is_callback:
            assert not ast.callbacks
            callbacks = ()
        else:
            callbacks = tuple(
                self.callback(c)
                for c in ast.callbacks
            )

        return Prototype(
            name=ast.declarator.name,
            parameter_declarations=tuple(
                self.parameter_declaration(p, is_callback)
                for p in ast.declarator.parameters
            ),
            has_return_value=(ast.declarator.type == 'function'),
            callbacks=callbacks,
        )

    def parameter_declaration(self, ast, is_callback):
        d = ParameterDeclaration(
            variable=Variable(name=ast.name),
            dimensions=len(ast.indexes),
        )
        if is_callback:
            self.check(d.dimensions == 0, CallbackParameterNotScalar(parameter=Snippet(ast)))
        return d

    def with_reference_actions(self, actions):
        actions = tuple(actions)
        assert all(
            a.reference is not None
            for a in actions
        )
        return self._replace(
            prev_reference_actions=self.prev_reference_actions + actions
        )

    def get_resolved_references(self):
        return {
            a.reference
            for a in self.prev_reference_actions
            if isinstance(a, ReferenceResolution)
        }

    @property
    def reference_definitions(self):
        return {
            a.reference: a
            for a in self.prev_reference_actions
            if isinstance(a, ReferenceDefinition)
        }

    def with_index_variable(self, variable):
        return self._replace(
            index_variables=self.index_variables + (variable,),
        )

    def with_loop(self):
        return self._replace(in_loop=True)

    @visitormethod
    def dimensions(self, e) -> int:
        pass

    def dimensions_IntLiteral(self, e):
        return 0

    def dimensions_Variable(self, e):
        try:
            return self.reference_definitions[e].dimensions
        except KeyError:
            return 0

    def dimensions_Subscript(self, e):
        try:
            return self.reference_definitions[e].dimensions
        except KeyError:
            array_dimensions = self.dimensions(e.array)
            if array_dimensions < 1:
                self.error(InvalidSubscript(array="<TODO>", index="<TODO>"))
                return 0
            return array_dimensions - 1

    @visitormethod
    def is_defined(self, e) -> bool:
        pass

    def is_defined_IntLiteral(self, e):
        return True

    def is_defined_Variable(self, e):
        return e in self.reference_definitions

    def is_defined_Subscript(self, e):
        return (
                e in self.reference_definitions
                or self.is_defined(e.array)
        )

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

    def statement(self, ast):
        return self._on_compile(self.STATEMENT_CLASSES[ast.statement_type], ast)

    @classvisitormethod
    def _on_compile(self, cls, ast):
        pass

    def _on_compile_object(self, cls, ast):
        return cls()

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
            ]).block(ast.body)
        )

    def _on_compile_Switch(self, cls, ast):
        value = self.scalar(ast.value)

        self.check(len(ast.cases) > 0, SwitchEmpty(switch=Location(ast)))

        cases = []
        labels = set()

        for case_ast in ast.cases:
            case = self.case(case_ast)
            cases.append(case)
            for l in case.labels:
                self.check(l not in labels, CaseLabelDuplicated(label=l))
                labels.add(l)

        return cls(
            value=value,
            cases=tuple(cases),
        )

    def case(self, ast):
        return Case(
            labels=[self.literal(l) for l in ast.labels],
            body=self.block(ast.body),
        )

    def _on_compile_If(self, cls, ast):
        return cls(
            condition=self.scalar(ast.condition),
            then_body=self.block(ast.then_body),
            else_body=self.block(ast.else_body) if ast.else_body is not None else None,
        )

    def _on_compile_Loop(self, cls, ast):
        return cls(
            body=self.with_loop().block(ast.body)
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
                parameter_declarations=(),
                has_return_value=False,
                callbacks=(),
            )
        else:
            if method.has_return_value:
                self.check(ast.return_value is not None, IgnoredReturnValue(name=method.name))
            else:
                self.check(ast.return_value is None, NoReturnValue(name=method.name))

        body_by_name = {}
        for cb in ast.callbacks:
            name = cb.declarator.name
            self.check(
                name in {c.name for c in method.callbacks},
                CallbackNotDeclared(name=method.name, callback=name),
            )
            self.check(name not in body_by_name, CallbackAlreadyImplemented(name=name))

        self.check(len(ast.arguments) == len(method.parameters), InvalidNumberOfArguments(
            name=method.name,
            n_parameters=len(method.parameters),
            n_arguments=len(ast.arguments),
        ))

        arguments = []

        for parameter_declaration, argument_ast in zip(method.parameter_declarations, ast.arguments):
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
        prepend_nodes = [
            CallbackStart(prototype),
        ]

        if prototype.has_return_value:
            append_nodes = []
        else:
            append_nodes = [CallbackEnd()]

        if ast is None:
            nodes = []
            if prototype.parameters:
                nodes.append(Write(prototype.parameters))
            if prototype.has_return_value:
                return_var = Variable("ans")
                nodes.append(Read([return_var]))
                nodes.append(Return(return_var))

            body = Block(tuple(
                itertools.chain(
                    prepend_nodes,
                    nodes,
                    append_nodes,
                )
            ))
        else:
            body = self.block(
                ast,
                prepend_nodes=prepend_nodes,
                append_nodes=append_nodes,
            )

        return CallbackImplementation(
            index=index,
            prototype=prototype,
            body=body
        )

    def statements(self, asts):
        inner = self
        for ast in asts:
            node = inner.statement(ast)
            yield node
            inner = inner.with_reference_actions(inner.reference_actions(node))

    def block(self, ast, prepend_nodes=(), append_nodes=()):
        return Block(
            children=tuple(
                itertools.chain(
                    prepend_nodes,
                    self.statements(ast.statements),
                    append_nodes,
                )
            )
        )

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

    EXPRESSION_TYPE_MAP = {
        "int_literal": IntLiteral,
        "subscript": Subscript,
        "variable": Variable,
    }

    def expression(self, ast):
        assert self.expression_type is not None
        ast = self._preprocess_expression_ast(ast)
        return self._on_compile(self.EXPRESSION_TYPE_MAP[ast.expression_type], ast)

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
