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
        | statement_type:'function' ~ declarator:callable_declarator ';'
        | statement_type:'callback' ~ declarator:callable_declarator body:block
        | statement_type:'main' ~ body:block
    ;

    return_type_declarator =
        '->' ~ @:type_expression
    ;
    
    callable_declarator =
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

    return_value_expression = '->' @:expression ;

    block_statement =
        | var_statement
        | statement_type:('input'|'output') ~ arguments:expression_list ';'
        | statement_type:('flush'|'break'|'continue'|'exit') ~ ';'
        | statement_type:'alloc' ~ arguments:expression_list ':' size:expression ';'
        | statement_type:'return' ~ value:expression ';'
        | statement_type:'call' ~ function_name:identifier
            '(' parameters:expression_list ')'
            return_value:[ return_value_expression ] ';'
        | statement_type:'if' ~ '(' condition:expression ')'
            then_body:block else_body:[ else_body ]
        | statement_type:'switch' ~ '(' value:expression ')' '{' cases:{ switch_case }* '}'
        | statement_type:'for' ~ '(' index:index_declaration ')' body:block
        | statement_type:'loop' ~ body:block
    ;

    else_body = 'else' ~ @:block ;

    expression_list = ','.{ expression }* ;

    switch_case =
        'case' '(' value:identifier ')' body:block
    ;

    atomic_expression =
        | expression_type:`int_literal` int_literal:INT
        | expression_type:`subscript` array:atomic_expression '[' index:expression ']'
        | expression_type:`reference` variable_name:identifier
        | '(' @:expression ')'
    ;
    
    expression =
        | expression_type:`binary`
            left:atomic_expression
            operator:('=='|'!='|'<'|'<='|'>'|'>=')
            right:atomic_expression
        | atomic_expression
    ;

    type_expression =
        | meta_type:`array` item_type:type_expression '[' ']'
        | meta_type:`scalar` base_type:'int'
    ;

    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/ ;

    STRING = '"' @:/([^"\n]|\\")*/ '"' ;
    INT = /0|-?[1-9][0-9]*/ ;

"""
