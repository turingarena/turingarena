#include <iostream>
#include <fstream>

#include "scanner.h"
#include "parser.hpp"

using Arena::Scanner;
using Arena::Parser;

int main(int argc, char **argv) {
	if(argc != 3) {
		std::cout << "Usage: " << argv[0] << " <descriptor_file> <command>" << std::endl;
		exit(EXIT_FAILURE);
	}

	auto descriptor_file = std::fstream(argv[1]);

	Scanner s { descriptor_file };
	Parser p { s };

	auto res = p.parse();

	std::cout << res << std::endl;

    return EXIT_SUCCESS;
}
