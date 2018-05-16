grammar_ebnf = r"""
    @@comments :: /\/\*((?!\*\/).)*\*\//
    @@eol_comments :: /\/\/.*$/
    @@left_recursion :: False
        
    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/;
    int_literal = /0|-?[1-9][0-9]*/;

    interface = function_declarations:{ callable_declaration }* ~ 'main' main_block:block $;
    
    callable_declaration = prototype:prototype ~ callbacks:callbacks_prototype_block;
    prototype = type:('function' | 'procedure') name:identifier '(' parameters:','.{ parameter_declaration }* ')';
    parameter_declaration = name:identifier indexes:{'[' ']'}*;

    callbacks_prototype_block = 'callbacks' ~ '{' @:{ callable_declaration }* '}' | ';' @:{} ;

    block = '{' statements:{ statement }* '}';
    
    callback_implementation = prototype:prototype body:block;
    callback_block = 'callbacks' ~ '{' @:{callback_implementation}* '}' | ';' @:{} ; 

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
            '(' parameters:','.{ expression }* ')'
            callbacks:callback_block
        ;

    return_exp = @:expression '=';
    else_body = 'else' ~ @:block;
    switch_case = 'case' ~ labels:','.{ int_literal }+ body:block;
    
    expression = or_expression;
    or_expression = 
        | and_expression
        | expression_type:`or` operands:'||'.{ and_expression }+
        ;
    and_expression =
        | comparison_expression
        | expression_type:`and` operands:'&&'.{ comparison_expression }+
        ;
    comparison_expression =
        | sum_expression
        | expression_type:`comparison` operands:( operators+:('=='|'!='|'<'|'<='|'>'|'>=') ).{ sum_expression }+
        ;
    sum_expression = 
        | mul_expression
        | expression_type:`sum` signs+:() operands:( signs+:('+'|'-') ).{ mul_expression }+
        | expression_type:`sum` { signs+:('+'|'-') operands+:mul_expression }+
        ;
    mul_expression =
        | atomic_expression
        | expression_type:`mul` operands:'*'.{ atomic_expression }+
        ;
    atomic_expression =
        | expression_type:`int_literal` int_literal:int_literal
        | expression_type:`reference` variable_name:identifier ~ indices:{ subscript }*
        | expression_type:`nested` '(' ~ expression:expression ')'
        ;
    
    subscript = '[' @:expression ']';
"""
