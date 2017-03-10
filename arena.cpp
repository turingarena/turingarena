#include <iostream>
#include <fstream>

#include "scanner.h"
#include "parser.hpp"

using Arena::Scanner;
using Arena::Parser;
using Arena::interface;

Arena::Algorithm& find_algorithm_or_die(const std::string& algorithm_name) {
	try {
		return interface.algorithms.at(algorithm_name);
	} catch (std::out_of_range& e) {
		std::cout << "Undefined algorithm: " << algorithm_name << std::endl;
		exit(EXIT_FAILURE);
	}
}

int main(int argc, char **argv) {
	if (argc < 3) {
		std::cout
				<< "Usage: "
				<< argv[0]
				<< " <descriptor_file> <command>"
				<< std::endl;
		exit(EXIT_FAILURE);
	}

	auto descriptor_file = std::fstream(argv[1]);

	Scanner s { descriptor_file };
	Parser p { s };

	p.parse();

	std::string command { argv[2] };

	if (command == "generate_support") {
		if (argc != 4) {
			std::cout
					<< "Usage: "
					<< argv[0]
					<< " <descriptor_file> "
					<< command
					<< " <algorithm>"
					<< std::endl;
			exit(EXIT_FAILURE);
		}

		std::string algorithm_name { argv[3] };
		find_algorithm_or_die(algorithm_name).generate_support(std::cout);
	} else if (command == "generate_stub") {
		if (argc != 4) {
			std::cout
					<< "Usage: "
					<< argv[0]
					<< " <descriptor_file> "
					<< command
					<< " <algorithm>"
					<< std::endl;
			exit(EXIT_FAILURE);
		}

		std::string algorithm_name { argv[3] };
		find_algorithm_or_die(algorithm_name).generate_stub(std::cout);
	} else {
		std::cout << "Unrecognized command: " << command << std::endl;
		exit(EXIT_FAILURE);
	}

	return EXIT_SUCCESS;
}
