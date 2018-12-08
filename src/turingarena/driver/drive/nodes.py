from collections import namedtuple

Step = namedtuple("Step", ["direction", "body"])
RequestLookahead = namedtuple("RequestLookahead", [])
CallbackStart = namedtuple("CallbackStart", ["prototype"])
CallbackEnd = namedtuple("CallbackEnd", [])
CallAccept = namedtuple("CallAccept", ["method", "arguments"])
CallReturn = namedtuple("CallReturn", ["return_value"])
CallCompleted = namedtuple("CallCompleted", [])
AcceptCallbacks = namedtuple("AcceptCallbacks", ["callbacks"])
ValueResolve = namedtuple("ValueResolve", ["value", "map"])
