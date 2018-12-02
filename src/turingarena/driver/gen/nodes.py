from collections import namedtuple

Print = namedtuple("Print", ["arguments"])
Flush = namedtuple("Flush", [])
Comment = namedtuple("Comment", ["text"])
VariableDeclaration = namedtuple("VariableDeclaration", ["variable", "dimensions"])
Alloc = namedtuple("Alloc", ["reference", "dimensions", "size"])

MethodTemplate = namedtuple("MethodTemplate", ["prototype", "description", "body"])
InterfaceTemplate = namedtuple("InterfaceTemplate", ["constants", "methods"])
