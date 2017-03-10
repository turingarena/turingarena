%skeleton "lalr1.cc" /* -*- C++ -*- */
%require "3.0"
%defines
%define parser_class_name { Parser }

%define api.token.constructor
%define api.value.type variant
%define parse.assert
%define api.namespace { Arena }
%code requires
{
    #include <iostream>
    #include <string>
    #include <vector>
    #include <stdint.h>
    #include "model.h"

    namespace Arena {
        using namespace std;
        class Scanner;
        extern Interface interface;
    }

}

%code top
{
    #include <iostream>
    #include "scanner.h"
    #include "parser.hpp"
    #include "location.hh"
    #include "model.h"
    
    namespace Arena {
        Interface interface;
    }
    
    using namespace Arena;

    // yylex() arguments are defined in parser.y
    static Parser::symbol_type yylex(Scanner &scanner) {
        return scanner.get_next_token();
    }
    
}

%lex-param { Arena::Scanner &scanner }
%parse-param { Arena::Scanner &scanner }

%locations
%define parse.trace
%define parse.error verbose

%define api.token.prefix {TOKEN_}

%token
  DATA "data"
  ALGORITHM "algorithm"
  <std::string> IDENTIFIER
  <BaseType> INT "int"
;

%token END 0 "end of file";

%start main

%%

%type <Interface> main;
main:
    interface {
      interface = std::move($interface);
    }
  ;

%type <Interface> interface;
interface:
    %empty { $$ = Interface {}; }
  | data_block_declaration interface { $$ = std::move($2); $$.data_blocks.insert($1); }
  | algorithm_declaration interface { $$ = std::move($2); $$.algorithms.insert($1); }
  ;

%type <std::pair<std::string, DataBlock>> data_block_declaration;
data_block_declaration:
    "data" IDENTIFIER data_block_body { $$ = make_pair($IDENTIFIER, $data_block_body); }
  ;

%type <DataBlock> data_block_body;
data_block_body:
    '{' variable_declaration_list[list] '}' { $$.variables = std::move($list); }
  ;

%type <std::pair<std::string, Algorithm>> algorithm_declaration;
algorithm_declaration:
    "algorithm" IDENTIFIER algorithm_body { $$ = make_pair($IDENTIFIER, $algorithm_body); }
  ;

%type <Algorithm> algorithm_body;
algorithm_body:
    '{' function_declaration_list '}' { $$.functions = $2; }
  ;

%type <std::unordered_map<std::string, AlgorithmFunction>> function_declaration_list;
function_declaration_list:
    %empty { }
  | function_declaration[f] function_declaration_list { auto name = $f.name; $$.insert(make_pair(name, std::move($f))); }

%type <AlgorithmFunction> function_declaration;
function_declaration:
    base_type IDENTIFIER '(' variable_declaration_list ')' function_body
{
  $$ = AlgorithmFunction { std::move($IDENTIFIER) };
}

%type <std::unordered_map<std::string, Variable>> variable_declaration_list;
variable_declaration_list:
    %empty { }
  | variable_declaration[decl] variable_declaration_list[rest] { $$ = std::move($rest); $$.insert($decl); }
  ;

%type <std::pair<std::string, Variable>> variable_declaration;
variable_declaration:
    base_type IDENTIFIER ';' {
      $$ = make_pair(
          std::string { $IDENTIFIER }, 
          Variable { std::move($base_type) }
      );
    }
  ;

%type <std::vector<ArraySpecification>> array_specification_list;
array_specification_list:
    %empty { }
  | '[' variable_reference ']' array_specification_list[rest] {
      $$ = std::move($rest);
      $$.push_back(ArraySpecification { });
    }
  ;

%type <BaseType> base_type;
base_type:
    "int" { $$ = $1; }
  ;

variable_reference:
    IDENTIFIER
  ;

function_body:
    ';'
  ;

%%

void Arena::Parser::error(const location &loc, const std::string &message) {
  cout << "Error: " << message << endl << "Location: " << loc << endl;
}
