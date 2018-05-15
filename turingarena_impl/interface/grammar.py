grammar_ebnf = r"""
    @@comments :: /\/\*((?!\*\/).)*\*\//
    @@eol_comments :: /\/\/.*$/
    @@left_recursion :: False
        
    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/;
    string_literal = '"' @:/([^"\n]|\\")*/ '"';
    int_literal = /0|-?[1-9][0-9]*/;

    interface = function_declarations:{ function_declaration }* ~ 'main' main_block:block $;
    
    function_prototype = type:('function' | 'procedure') name:identifier '(' parameters:','.{ parameter_type }* ')';
    function_declaration = prototype:function_prototype ~ (';' | callbacks:callback_prototype_block);
    callback_declaration = prototype:function_prototype ~ ';';
        
    parameter_type = name:identifier indexes:{'[' ']'}*;
    callback_prototype_block = 'callbacks' '{' @:{callback_declaration}* '}';

    block = '{' statements:{ block_statement }* '}';
    
    callback_implementation = prototype:function_prototype body:block;
    callback_block = 'callbacks' '{' @:{callback_implementation}* '}'; 

    block_statement =
        | statement_type:('read' | 'write') ~ arguments:','.{ expression }* ';'
        | statement_type:('checkpoint' | 'break' | 'exit') ~ ';'
        | statement_type:'return' ~ value:expression ';'
        | statement_type:'if' ~ condition:expression then_body:block else_body:[ else_body ]
        | statement_type:'switch' ~ value:expression '{' cases:{ switch_case }+ '}'
        | statement_type:'for' ~ index:identifier 'to' range:expression body:block
        | statement_type:'loop' ~ body:block
        | statement_type:'call' ~ [return_value:return_exp] name:identifier '(' parameters:','.{ expression }* ')' (callbacks:callback_block | ';')
        ;

    return_exp = @:expression '=';
    else_body = 'else' ~ @:block;
    switch_case = labels:','.{ int_literal }+ body:block;
    
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
        | expression_type:`reference` variable_name:identifier ~ indices:{ subscript }*
        | expression_type:`nested` '(' ~ expression:expression ')'
        ;
    
    subscript = '[' @:expression ']';
"""
