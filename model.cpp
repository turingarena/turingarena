#include "model.h"

#include <iostream>

using std::string;

std::ostream& Arena::operator<<(std::ostream& out, const Arena::Interface& interface) {
	int level = 0;
	for(auto& target : interface.algorithms) {
		out << string(level, ' ') << "target " << target.first << " {" << std::endl;
		out << target.second;
		out << string(level, ' ') << "}" << std::endl;
	}
	return out;
}

std::ostream& Arena::operator<<(std::ostream& out, const Arena::Algorithm& algorithm) {
	int level = 4;
	for(auto& function : algorithm.functions) {
		out << string(level, ' ') << "function " << function.first << " {" << std::endl;
		//out << function.second;
		out << string(level, ' ') << "}" << std::endl;
	}
	return out;
}

void Arena::Variable::generate_stub_global(std::ostream& out) {
	out << "extern int " << name << ";" << std::endl;
}

void Arena::Algorithm::generate_support(std::ostream& out) {
	out << "support code..." << std::endl;
}

void Arena::Algorithm::generate_stub(std::ostream& out) {
	for(auto& var : global_input.variables) {
		var.second.generate_stub_global(out);
	}
}
