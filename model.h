/*
 * model.h
 *
 *  Created on: 22 gen 2017
 *      Author: max
 */

#ifndef MODEL_H_
#define MODEL_H_

#include <vector>
#include <string>
#include <unordered_map>

namespace Arena {

using std::vector;
using std::unordered_map;
using std::string;

enum BaseType {
	INT
};

struct ArraySpecification {

};

struct Variable {
	string name;
	BaseType base_type;
	vector<ArraySpecification> array_specifications;
};

struct VariableSet {
	unordered_map<string, Variable> variables;
};

struct TargetFunction {
	string name;
	vector<Variable> parameters;

	void generate_target_code(std::ostream& out);
};

struct Target {
	unordered_map<string, TargetFunction> functions;
};

std::ostream& operator<< (std::ostream& out, const Target& interface);

struct Interface {
	unordered_map<string, Target> targets;
};

std::ostream& operator<< (std::ostream& out, const Interface& interface);

} // namespace Arena

#endif /* MODEL_H_ */
