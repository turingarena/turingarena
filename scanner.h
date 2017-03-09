#ifndef SCANNER_H
#define SCANNER_H

#if ! defined(yyFlexLexerOnce)
#undef yyFlexLexer
#define yyFlexLexer Arena_FlexLexer
#include <FlexLexer.h>
#endif

#undef YY_DECL
#define YY_DECL Arena::Parser::symbol_type Arena::Scanner::get_next_token()

#include "parser.hpp"

namespace Arena {

class Scanner: public yyFlexLexer {
public:
	Scanner(istream& s) {
		yyrestart(s);
	}
	virtual ~Scanner() {
	}
	virtual Parser::symbol_type get_next_token();

private:
};

}

#endif
