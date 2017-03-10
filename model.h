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

	void generate_stub_global(std::ostream& out);
};

struct DataBlock {
	unordered_map<string, Variable> variables;
};

struct AlgorithmFunction {
	string name;
};

struct Algorithm {
	unordered_map<string, AlgorithmFunction> functions;
	DataBlock global_input;

	void generate_support(std::ostream& out);
	void generate_stub(std::ostream& out);
};

std::ostream& operator<< (std::ostream& out, const Algorithm& algorithm);

struct Interface {
	unordered_map<string, Algorithm> algorithms;
	unordered_map<string, DataBlock> data_blocks;
};

std::ostream& operator<< (std::ostream& out, const Interface& interface);

} // namespace Arena

#endif /* MODEL_H_ */
