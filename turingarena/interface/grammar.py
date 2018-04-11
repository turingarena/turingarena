grammar_ebnf = r"""
    @@comments :: /\/\*((?!\*\/).)*\*\//
    @@eol_comments :: /\/\/.*$/
    @@left_recursion :: False
    
    interface = statements:{ interface_statement }* $ ;
    
    interface_statement =
        | var_statement
        | statement_type:'function' ~ declarator:callable_declarator ';'
        | statement_type:'callback' ~ declarator:callable_declarator body:block
        | statement_type:'init' ~ body:block
        | statement_type:'main' ~ body:block
    ;

    return_type_declarator =
        '->' @:type_expression
    ;
    
    callable_declarator =
        name:identifier '('
            parameters:','.{ parameter_declaration }*
        ')'
        return_type:[ return_type_declarator ]
    ;

    var_statement =
        statement_type:'var' ~ type:type_expression declarators:','.{ declarator }+ ';'
    ;
    
    declarator = name:identifier ;

    index_declaration =
        declarator:declarator ':' range:expression
    ;

    parameter_declaration = type:type_expression declarator:declarator ;

    block = '{' statements:{ block_statement }* '}' ;

    return_value_expression = '->' ~ @:expression ;

    block_statement =
        | var_statement
        | statement_type:('read'|'write') ~ arguments:expression_list ';'
        | statement_type:('checkpoint'|'flush'|'break'|'continue'|'exit') ~ ';'
        | statement_type:'alloc' ~ arguments:expression_list ':' size:expression ';'
        | statement_type:'return' ~ value:expression ';'
        | statement_type:'call' ~ function_name:identifier
            '(' parameters:expression_list ')'
            return_value:[ return_value_expression ] ';'
        | statement_type:'if' ~ '(' condition:expression ')'
            then_body:block else_body:[ else_body ]
        | statement_type:'switch' ~ '(' value:expression ')' '{' cases:{ switch_case }+ default:[default_case] '}'
        | statement_type:'for' ~ '(' index:index_declaration ')' body:block
        | statement_type:'loop' ~ body:block
    ;

    else_body = 'else' ~ @:block ;

    expression_list = ','.{ expression }* ;

    default_case = 
        'default' body:block
    ;

    switch_case =
        'case' labels:','.{expression}+ body:block
    ;
    
    expression = or_expression ;
    or_expression = 
        |
            expression_type:`or`
            operands:and_expression
            { '||' operands:and_expression }+
        | and_expression
    ;
    and_expression =
        |
            expression_type:`and`
            operands:comparison_expression
            { '&&' operands:comparison_expression }+
        | comparison_expression
    ;
    comparison_expression =
        |
            expression_type:`comparison`
            operands:sum_expression
            {
                operators+:('=='|'!='|'<'|'<='|'>'|'>=')
                operands:sum_expression
            }+
        | sum_expression
    ;
    sum_expression = 
        |
            expression_type:`sum`
            signs:() operands:mul_expression
            { signs:('+'|'-') operands:mul_expression }+
        |
            expression_type:`sum`
            signs+:('+'|'-') operands:mul_expression
            { signs+:('+'|'-') operands:mul_expression }*
        | mul_expression
    ;
    mul_expression =
        |
            expression_type:`mul`
            operands:atomic_expression
            { '*' operands:atomic_expression }+
        | atomic_expression
    ;
    atomic_expression =
        |
            expression_type:`int_literal`
            int_literal:INT
        |
            expression_type:`reference`
            variable_name:identifier ~ indices:{ subscript }*
        |
            expression_type:`nested`
            '(' ~ expression:expression ')'
    ;
    subscript = '[' @:expression ']' ;

    type_expression = 'int' ~ dimensions:{ '[' ']' }* ;

    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/ ;

    STRING = '"' @:/([^"\n]|\\")*/ '"' ;
    INT = /0|-?[1-9][0-9]*/ ;

"""
