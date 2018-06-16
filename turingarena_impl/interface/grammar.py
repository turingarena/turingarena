grammar_ebnf = r"""
    @@comments :: /\/\*((?!\*\/).)*\*\//
    @@eol_comments :: /\/\/.*$/
    @@left_recursion :: False
        
    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/;
    int_literal = /0|-?[1-9][0-9]*/;

    interface = method_declarations:{ callable_declaration }* ~ 'main' main_block:block $;
    
    callable_declarator =
        type:('function' | 'procedure')
        ~
        name:identifier
        '(' parameters:','.{ parameter_declaration }* ')'
        ;
    parameter_declaration = name:identifier indexes:{'[' ']'}*;

    callable_declaration = declarator:callable_declarator callbacks:callback_declarations ;

    callback_declarations = 'callbacks' ~ '{' @:{ callable_declaration }* '}' | ';' @:{} ;

    block = '{' statements:{ statement }* '}';
    
    statement =
        | statement_type:('read' | 'write') ~ arguments:','.{ expression }* ';'
        | statement_type:('checkpoint' | 'break' | 'exit') ~ ';'
        | statement_type:'return' ~ value:expression ';'
        | statement_type:'if' ~ condition:expression then_body:block else_body:[ else_body ]
        | statement_type:'switch' ~ value:expression '{' cases:{ switch_case }+ '}'
        | statement_type:'for' ~ index:identifier 'to' range:expression body:block
        | statement_type:'loop' ~ body:block
        | statement_type:'call' ~
            return_value:[ return_exp ]
            name:identifier
            '(' arguments:','.{ expression }* ')'
            callbacks:callback_implementations
        ;

    callback_implementation = declarator:callable_declarator body:block;
    callback_implementations = 'callbacks' ~ '{' @:{callback_implementation}+ '}' | ';' @:{} ; 

    return_exp = @:expression '=';
    else_body = 'else' ~ @:block;
    switch_case = 'case' ~ labels:','.{ int_literal }+ body:block;
    
    expression = or_expression;
    or_expression = 
        | expression_type:`or` operands:and_expression { '||' operands:and_expression }+
        | and_expression
        ;
    and_expression =
        | expression_type:`and` operands:comparison_expression { '&&' operands:comparison_expression }+
        | comparison_expression
        ;
    comparison_expression =
        | expression_type:`comparison` operands:sum_expression { operators+:('=='|'!='|'<'|'<='|'>'|'>=') operands:sum_expression }+
        | sum_expression
        ;
    sum_expression = 
        | expression_type:`sum` signs:() operands:mul_expression { signs:('+'|'-') operands:mul_expression }+
        | expression_type:`sum` signs+:('+'|'-') operands:mul_expression { signs+:('+'|'-') operands:mul_expression }*
        | mul_expression
        ;
    mul_expression =
        | expression_type:`mul` operands:atomic_expression { '*' operands:atomic_expression }+
        | atomic_expression
        ;
    atomic_expression =
        | expression_type:`int_literal` int_literal:int_literal
        | expression_type:`reference_subscript` variable_name:identifier ~ indices:{ subscript }*
        | expression_type:`nested` '(' ~ expression:expression ')'
        ;
    
    subscript = '[' @:expression ']';
"""
