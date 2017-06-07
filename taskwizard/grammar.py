grammar_ebnf = r"""
    @@comments :: /\/\*(.|\n|\r)*\*\//
    @@eol_comments :: /\/\/.*$/

    task = task_items:{ task_item }* ;
    
    task_item = interface_definition ;
    
    interface_definition =
        'interface' ~ name:identifier '{'
            interface_items:{ interface_item }*
        '}'
    ;
    
    interface_item =
        | global_declaration
        | const_declaration
        | function_declaration
        | callback_definition
        | main_definition
    ;

    function_declaration =
        'function' ~ return_type:return_type declarator:function_declarator '('
            parameters:parameter_declaration_list
        ')'
        ';'
    ;
    
    function_declarator = name:identifier ;

    callback_definition =
        'callback' ~ return_type:return_type name:identifier '('
            parameters:parameter_declaration_list
        ')'
        block:block
    ;

    main_definition =
        'main' ~ block:block
    ;

    global_declaration =
        'global' ~ type:type declarators:declarator_list ';'
    ;
    
    local_declaration =
        'local' ~ type:type declarators:declarator_list ';'
    ;
    
    const_declaration =
        'const' ~ type:type declarators:init_declarator_list ';'
    ;
    
    index_declaration =
        declarator:index_declarator ':' range:range
    ;

    parameter_declaration_list = ','.{ parameter_declaration }* ;

    parameter_declaration = type:type declarator:declarator ;

    init_declarator_list = ','.{ init_declarator }+;

    init_declarator = declarator:declarator '=' expression:expression ;
        
    declarator_list = ','.{ declarator }+;

    declarator = name:identifier ;
    
    index_declarator = name:identifier ;

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
        | if_statement
        | switch_statement
        | for_statement
        | do_statement
        | break_statement
        | continue_statement
        | return_statement
    ;

    expression_list = ','.{ expression }* ;

    input_statement =
        'input' ~ arguments:expression_list ';'
    ;

    output_statement =
        'output' ~ arguments:expression_list ';'
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
        'if' ~ '(' condition:expression ')' then_block:block
        [ 'else' ~ else_block:block ]
    ;

    switch_statement =
        'switch' ~ '(' expression:expression ')' '{'
            cases:{ switch_case }*
        '}'
    ;

    switch_case =
        'case' '(' value:identifier ')' block:block
    ;

    for_statement =
        'for' ~ '(' index:index_declaration ')' block:block
    ;

    do_statement =
        'do' ~ block:block
    ;
    
    break_statement = 'break' ~ ';' ;

    continue_statement = 'continue' ~ ';' ;

    return_statement = 'return' ~ expression:expression ';' ;

    range =
        start:expression '..' end:expression
    ;

    expression =
        | subscript_expression
        | variable_expression
        | int_literal_expression
    ;
    
    subscript_expression =
        array:expression '[' index:expression ']'
    ;
    
    variable_expression = variable_name:identifier ;

    variable_expression_index = '[' @:expression ']' ;
    
    int_literal_expression = value:INT;

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
    
    return_type =
        | @:type
        | 'void'
    ;

    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/ ;

    STRING = '"' @:/([^"\n]|\\")*/ '"' ;
    INT = /[1-9][0-9]*/ ;

"""


