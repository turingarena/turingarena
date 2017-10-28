grammar_ebnf = r"""
    @@comments :: /\/\*(.|\n|\r)*\*\//
    @@eol_comments :: /\/\/.*$/

    protocol = body:protocol_body $ ;
    
    protocol_body = statements:{ protocol_statement }* ;
    
    protocol_statement =
        statement_type:'interface' ~ name:identifier '{'
            body:interface_body
        '}'
    ;
    
    interface_body = statements:{ interface_statement }* ;
    
    interface_statement =
        | var_statement
        | statement_type:'function' ~ declarator:signature_declarator ';'
        | statement_type:'callback' ~ declarator:signature_declarator body:block
        | statement_type:'main' ~ body:block
    ;

    return_type_declarator =
        '->' ~ @:type_expression
    ;
    
    signature_declarator =
        name:identifier '('
            parameters:','.{ parameter_declaration }*
        ')'
        return_type:[ return_type_declarator ]
    ;

    var_statement =
        statement_type:'var' ~ type_expression:type_expression declarators:','.{ declarator }+ ';'
    ;
    
    declarator = name:identifier ;

    index_declaration =
        declarator:declarator ':' range:expression
    ;

    parameter_declaration = type_expression:type_expression declarator:declarator ;

    block = '{' statements:{ block_statement }* '}' ;

    block_statement =
        | var_statement
        | statement_type:('input'|'output') ~ arguments:expression_list ';'
        | statement_type:('flush'|'break'|'continue'|'exit') ~ ';'
        | statement_type:'alloc' ~ arguments:expression_list ':' size:expression ';'
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

    expression =
        | expression_type:`int_literal` int_literal:INT
        | expression_type:`bool_literal` bool_literal:BOOL
        | expression_type:`subscript` array:expression '[' index:expression ']'
        | expression_type:`reference` variable_name:identifier
    ;

    type_expression =
        | meta_type:`array` item_type:type_expression '[' ']'
        | meta_type:'enum' ~ underlying_type:[underlying_type_declaration]
            '{' items:','.{ identifier }* '}'
        | meta_type:`scalar` base_type:base_type
    ;
    
    base_type = ('int'|'bool') ;
    
    underlying_type_declaration = ':' @:base_type ;

    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/ ;

    BOOL = /(0|1)/ ;
    STRING = '"' @:/([^"\n]|\\")*/ '"' ;
    INT = /0|-?[1-9][0-9]*/ ;

"""
