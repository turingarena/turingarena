grammar_ebnf = r"""
    @@comments :: /\/\*((?!\*\/).)*\*\//
    @@eol_comments :: /\/\/.*$/
    @@left_recursion :: False
    
    identifier = /[a-zA-Z_][0-9a-zA-Z_]*/;
    string_literal = '"' @:/([^"\n]|\\")*/ '"';
    int_literal = /0|-?[1-9][0-9]*/;

    interface = functions_declarations:function_declarations ~ main_block:block $;
    
    function_prototype = return_type:('int' | 'void') name:identifier '(' parameters:','.{ parameter_type }* ')';
    function_declarations = functions:{ function_declaration }*;
    function_declaration = prototype:function_prototype ~ ';';
        
    parameter_type = 
        | type:`callback` prototype:function_prototype
        | type:`variable` 'int' name:identifier indexes:{'[' ']'}*
        ;

    block = '{' statements:{ block_statement }* '}';

    block_statement =
        | statement_type:('read' | 'write') ~ arguments:','.{ expression }* ';'
        | statement_type:('checkpoint' | 'break' | 'continue' | 'exit') ~ ';'
        | statement_type:'return' ~ value:expression ';'
        | statement_type:'if' ~ condition:expression then_body:block else_body:[ else_body ]
        | statement_type:'switch' ~ value:expression '{' cases:{ switch_case }+ '}'
        | statement_type:'for' ~ index:identifier 'to' range:identifier body:block
        | statement_type:'loop' ~ body:block
        | statement_type:'call' ~ [return_variable:identifier '='] name:identifier '(' parameters:','.{ expression }* ')' ';'
        | statement_type:`callback` prototype:function_prototype ~ (body:block | 'default' ';')
        ;

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
