from collections.__init__ import namedtuple

RequestSignature = namedtuple("RequestSignature", ["command"])
CallRequestSignature = namedtuple("CallRequestSignature", ["command", "method_name"])