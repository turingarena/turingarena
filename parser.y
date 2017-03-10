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
    }
}

%code top
{
    #include <iostream>
    #include "scanner.h"
    #include "parser.hpp"
    #include "location.hh"
    #include "model.h"
    
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
  ALGORITHM "algorithm"
  <std::string> IDENTIFIER
  <BaseType> INT "int"
;

%token END 0 "end of file";

%start main

%%

main:
    interface {
      for(auto algorithm : $interface.algorithms) {
        for(auto fun : algorithm.second.functions) {
          fun.second.generate_code(std::cout);
        }
      }
    }
  ;

%type <Interface> interface;
interface:
    %empty { $$ = Interface {}; }
  | declaration interface { $$ = std::move($2); $$.algorithms.insert($1); }
  ;
  
%type <std::pair<std::string, Algorithm>> declaration;
declaration:
    algorithm_declaration { $$ = std::move($1); }
  ;

%type <std::pair<std::string, Algorithm>> algorithm_declaration;
algorithm_declaration:
    "algorithm" IDENTIFIER algorithm_body { $$ = make_pair($2, $3); }
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
  $$ = AlgorithmFunction { std::move($IDENTIFIER), std::move($variable_declaration_list) };
}

%type <std::vector<Variable>> variable_declaration_list;
variable_declaration_list:
    %empty { }
  | variable_declaration_nonempty_list { $$ = std::move($1); }
  ;

%type <std::vector<Variable>> variable_declaration_nonempty_list;
variable_declaration_nonempty_list:
    variable_declaration { $$.push_back($1); }
  | variable_declaration ',' variable_declaration_nonempty_list { $$ = std::move($3); $$.push_back($1); }
  ;

%type <Variable> variable_declaration;
variable_declaration:
    base_type IDENTIFIER array_specification_list {
      $$ = Variable { std::move($IDENTIFIER), std::move($base_type), std::move($array_specification_list) };
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
