import grako


class AbstractSyntaxNode:

    def __init__(self, ast):
        self.ast = ast
        self.parseinfo = ast.parseinfo


grammar_ebnf = r"""
    @@comments :: /\/\*(.|\n|\r)*\*\//
    @@eol_comments :: /\/\/.*$/

    unit =
        interfaces:{ interface_definition }*
    ;
    
    interface_definition(InterfaceDefinition) =
        'interface' ~ name:identifier '{' {
            | variables+:global_declaration
            | consts+:const_declaration
            | functions+:function_definition
            | callbacks+:callback_definition
            | main_definition:main_definition
        }* '}'
    ;
    
    function_definition(FunctionDefinition) =
        'function' ~ return_type:return_type name:identifier '('
            parameters:parameter_declaration_list
        ')'
        ';'
    ;

    callback_definition(CallbackDefinition) =
        'callback' ~ return_type:return_type name:identifier '('
            parameters:parameter_declaration_list
        ')'
        block:block
    ;

    main_definition(ProtocolDefinition) =
        'main' ~ block:block
    ;

    global_declaration(GlobalDefinition) =
        'global' ~ type:type declarators:declarator_list ';'
    ;
    
    local_declaration =
        'local' ~ type:type declarators:declarator_list ';'
    ;
    
    const_declaration =
        'const' ~ type:type declarators:init_declarator_list ';'
    ;
    
    parameter_declaration_list = ','.{ parameter_declaration }* ;

    parameter_declaration = type:type declarator:declarator ;

    init_declarator_list = ','.{ init_declarator }+;

    init_declarator = declarator:declarator '=' expression:expression ;
        
    declarator_list = ','.{ declarator }+;

    declarator = name:identifier ;
    
    block = '{' block_items:{ block_item }* '}' ;

    block_item =
        | local_declaration
        | const_declaration
        | statement
    ;
    
    statement =
        | input_statement
        | output_statement
        | alloc_statement
        | call_statement
        | for_statement
        | do_statement
        | switch_statement
        | break_statement
        | continue_statement
        | return_statement
    ;

    expression_list = ','.{ expression }* ;

    input_statement(InputStatement) =
        'input' ~ arguments:expression_list ';'
    ;

    output_statement(OutputStatement) =
        'output' ~ arguments:expression_list ';'
    ;

    alloc_statement(AllocStatement) =
        'alloc' ~ arguments:expression_list ':' range:range ';'
    ;

    call_statement(CallStatement) =
        'call' ~ function_name:identifier '('
            parameters:','.{ expression }*
        ')'
        [ '->' return_value:expression ] 
        ';'
    ;

    for_statement(ForStatement) =
        'for' ~ '(' index:identifier ':' range:range ')' block:block
    ;

    do_statement(DoStatement) =
        'do' ~ block:block
    ;
    
    switch_statement(SwitchStatement) =
        'switch' ~ '(' expression:expression ')' '{'
            cases:{ switch_case }*
        '}'
    ;

    switch_case(SwitchCase) =
        'case' '(' value:identifier ')' block:block
    ;

    break_statement(BreakStatement) = 'break' ';' ;

    continue_statement(ContinueStatement) = 'continue' ';' ;

    return_statement(ReturnStatement) = 'return' expression:expression ';' ;

    range(Range) =
        start:expression '..' end:expression
    ;

    expression(Expression) =
        | variable_expression
        | int_literal_expression
    ;
    
    variable_expression(VariableExpression) =
        variable_name:identifier
        indexes:{ variable_expression_index }*
    ;

    variable_expression_index = '[' @:expression ']' ;
    
    int_literal_expression = value:INT;

    base_type =
        | 'int'
        | 'int64'
        | 'bool'
    ;
    
    type =
        | enum_type
        | array_type
    ;
    
    array_type =
        base_type:base_type ~ dimensions:{ '[' ']' }*
    ;
    
    enum_type =
        'enum' ~ '{'
            items:','.{ identifier }*
        '}'
    ;

    return_type =
        | @:type
        | 'void'
    ;

    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/ ;

    STRING = '"' @:/([^"\n]|\\")*/ '"' ;
    INT(int) = /[1-9][0-9]*/ ;

"""

grammar = grako.compile(grammar_ebnf)


def parse(*args, **kwargs):
    return grammar.parse(*args, **kwargs)
