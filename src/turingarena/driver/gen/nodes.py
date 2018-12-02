from collections.__init__ import namedtuple

Print = namedtuple("Print", ["arguments"])
Flush = namedtuple("Flush", [])
Comment = namedtuple("Comment", ["text"])

MethodTemplate = namedtuple("MethodTemplate", ["prototype", "description", "body"])
InterfaceTemplate = namedtuple("InterfaceTemplate", ["constants", "methods"])
