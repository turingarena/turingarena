grammar_ebnf = r"""
    @@comments :: /\/\*(.|\n|\r)*\*\//
    @@eol_comments :: /\/\/.*$/

    unit = statements:{ unit_statement }* $ ;
    
    unit_statement =
        statement_type:'interface' ~ name:identifier '{'
            statements:{ interface_statement }*
        '}'
    ;
    
    signature =
        declarator:function_declarator '('
            parameters:parameter_declaration_list
        ')'
        return_type:[ return_type_declarator ]
    ;

    return_type_declarator =
        '->' ~ @:type
    ;
    
    function_declarator = name:identifier ;

    interface_statement =
        | var_statement
        | statement_type:'function' ~ >signature ';'
        | statement_type:'callback' ~ >signature body:block
        | statement_type:'main' ~ body:block
    ;

    var_statement =
        statement_type:'var' ~ type:type declarators:declarator_list ';'
    ;
    
    index_declaration =
        declarator:declarator ':' range:range
    ;

    parameter_declaration_list = ','.{ parameter_declaration }* ;

    parameter_declaration = type:type declarator:declarator ;

    declarator_list = ','.{ declarator }+ ;

    declarator = name:identifier ;

    block = '{' statements:{ block_statement }* '}' ;

    block_statement =
        | var_statement
        | statement_type:('input'|'output') ~ arguments:expression_list ';'
        | statement_type:('flush'|'break'|'continue'|'exit') ~ ';'
        | statement_type:'alloc' ~ arguments:expression_list ':' range:range ';'
        | statement_type:'return' ~ value:expression ';'
        | statement_type:'call' ~ function_name:identifier
            '(' parameters:expression_list ')'
            [ '->' return_value:expression ] ';'
        | statement_type:'if' ~ '(' condition:expression ')'
            then_body:block [ 'else' ~ else_body:block ]
        | statement_type:'switch' ~ '(' value:expression ')' '{' cases:{ switch_case }* '}'
        | statement_type:'for' ~ '(' index:index_declaration ')' body:block
        | statement_type:'loop' ~ body:block
    ;

    expression_list = ','.{ expression }* ;

    switch_case =
        'case' '(' value:identifier ')' body:block
    ;

    range =
        start:expression '..' end:expression
    ;

    expression =
        | int_literal_expression
        | subscript_expression
        | variable_expression
    ;
    
    subscript_expression =
        array:expression '[' index:expression ']'
    ;
    
    variable_expression = variable_name:identifier ;

    int_literal_expression = int_literal:INT;
    bool_literal_expression = bool_literal:BOOL;

    type =
        | array_type
        | enum_type
        | scalar_type 
    ;
    
    array_type = item_type:type '[' ']' ;
    
    enum_type =
        'enum' ~ '{'
            items:','.{ identifier }*
        '}'
    ;

    scalar_type = base:base_type ;

    base_type =
        | 'int'
        | 'int64'
        | 'bool'
    ;

    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/ ;

    BOOL = /(False|True)/ ;
    STRING = '"' @:/([^"\n]|\\")*/ '"' ;
    INT = /0|-?[1-9][0-9]*/ ;

"""
