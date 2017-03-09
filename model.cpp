#include "model.h"

#include <iostream>

using std::string;

std::ostream& Arena::operator<<(std::ostream& out, const Arena::Interface& interface) {
	int level = 0;
	for(auto& target : interface.targets) {
		out << string(level, ' ') << "target " << target.first << " {" << std::endl;
		out << target.second;
		out << string(level, ' ') << "}" << std::endl;
	}
	return out;
}

std::ostream& Arena::operator<<(std::ostream& out, const Arena::Target& target) {
	int level = 4;
	for(auto& function : target.functions) {
		out << string(level, ' ') << "function " << function.first << " {" << std::endl;
		//out << function.second;
		out << string(level, ' ') << "}" << std::endl;
	}
	return out;
}

void Arena::TargetFunction::generate_target_code(std::ostream& out) {
	for(auto& parameter : parameters) {
		int dims = parameter.array_specifications.size();
		for(int i = 0; i < dims; i++) {
			out << "for(";
			out << "int " << "index" << i << "; ";
			out << "index" << i << " < 10; ";
			out << "index" << i << "++";
			out << ") {" << std::endl;
		}

		switch (parameter.base_type) {
			case INT:
				out << "scanf(\"%d\", " << "&" << parameter.name << ");" << std::endl;
				break;
			default:
				throw std::runtime_error("Unsupported base type.");
		}

		for(int i = 0; i < dims; i++) {
			out << "}" << std::endl;
		}
	}
}
