%{
	#include <iostream>
	#include <cstdlib>
	#include "scanner.h"
	#include "parser.hpp"
	#include "location.hh"

  #include "model.h"
  
	using namespace std;
	using namespace Arena;
%}

%option nodefault
%option noyywrap
%option c++
%option yyclass="Scanner"
%option prefix="Arena_"

%%

[ \t\n] ;

algorithm { return Parser::make_ALGORITHM(location()); }
data { return Parser::make_DATA(location()); }
int { return Parser::make_INT(BaseType::INT, location()); }

[a-zA-Z][a-zA-Z0-9]* {
  return Parser::make_IDENTIFIER(std::string(yytext), location());
} 

<<EOF>> {
  return Parser::make_END(location());
}

. {
  return Parser::symbol_type((Parser::token_type) yytext[0], location());
}

%%
