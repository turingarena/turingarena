from collections import namedtuple

RequestSignature = namedtuple("RequestSignature", ["command"])
CallRequestSignature = namedtuple("CallRequestSignature", ["command", "method_name"])