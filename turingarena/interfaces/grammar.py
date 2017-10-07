grammar_ebnf = r"""
    @@comments :: /\/\*(.|\n|\r)*\*\//
    @@eol_comments :: /\/\/.*$/

    unit = unit_items:{ unit_item }* $ ;
    
    unit_item = interface_definition ;
    
    interface_definition =
        'interface' ~ name:identifier '{'
            interface_items:{ interface_item }*
        '}'
    ;
    
    interface_item =
        | variable_declaration
        | function_declaration
        | callback_declaration
        | main_declaration
    ;

    function_declaration =
        'function' ~ declarator:function_declarator '('
            parameters:parameter_declaration_list
        ')'
        [ '->' return_type:type ]
        ';'
    ;
    
    callback_declaration =
        'callback' ~ declarator:function_declarator '('
            parameters:parameter_declaration_list
        ')'
        return_type:[ return_type_declarator ]
        body:block
    ;
    
    return_type_declarator =
        '->' ~ @:type
    ;

    function_declarator = name:identifier ;

    main_declaration =
        'main' ~ body:block
    ;

    variable_declaration =
        'var' ~ type:type declarators:declarator_list ';'
    ;
    
    index_declaration =
        declarator:declarator ':' range:range
    ;

    parameter_declaration_list = ','.{ parameter_declaration }* ;

    parameter_declaration = type:type declarator:declarator ;

    declarator_list = ','.{ declarator }+ ;

    declarator = name:identifier ;

    block = '{' block_items:{ block_item }* '}' ;

    block_item =
        | variable_declaration
        | statement
    ;
    
    statement =
        | input_statement
        | output_statement
        | flush_statement
        | alloc_statement
        | call_statement
        | if_statement
        | switch_statement
        | for_statement
        | loop_statement
        | break_statement
        | continue_statement
        | return_statement
        | exit_statement
    ;

    expression_list = ','.{ expression }* ;

    input_statement =
        'input' ~ arguments:expression_list ';'
    ;

    output_statement =
        'output' ~ arguments:expression_list ';'
    ;
    
    flush_statement =
        'flush' ~ arguments:() ';'
    ;

    alloc_statement =
        'alloc' ~ arguments:expression_list ':' range:range ';'
    ;

    call_statement =
        'call' ~ function_name:identifier '('
            parameters:','.{ expression }*
        ')'
        [ '->' return_value:expression ] 
        ';'
    ;
    
    if_statement =
        'if' ~ '(' condition:expression ')' then_body:block
        [ 'else' ~ else_body:block ]
    ;

    switch_statement =
        'switch' ~ '(' value:expression ')' '{'
            cases:{ switch_case }*
        '}'
    ;

    switch_case =
        'case' '(' value:identifier ')' body:block
    ;

    for_statement =
        'for' ~ '(' index:index_declaration ')' body:block
    ;

    loop_statement =
        'loop' ~ body:block
    ;
    
    break_statement = 'break' ~ ';' ;

    continue_statement = 'continue' ~ ';' ;

    return_statement = 'return' ~ value:expression ';' ;
    
    exit_statement = 'exit' ~ arguments:() ';' ;

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
