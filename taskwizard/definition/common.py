from taskwizard.definition.syntax import AbstractSyntaxFragment


class Identifier(AbstractSyntaxFragment):

    grammar = r"""
        identifier = /[a-zA-Z_][0-9a-zA-Z_]*/ ;
    """


class Literals(AbstractSyntaxFragment):

    grammar = r"""
        STRING = '"' @:/([^"\n]|\\")*/ '"' ;
        INT::int = /[1-9][0-9]*/ ;
    """


class Types(AbstractSyntaxFragment):

    grammar = r"""
        type =
        | 'int'
        | 'bool'
        ;

        return_type =
        | @:type
        | 'void'
        ;
    """