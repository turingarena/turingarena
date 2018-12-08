from collections import namedtuple

Step = namedtuple("Step", ["direction", "body"])
RequestLookahead = namedtuple("RequestLookahead", [])
CallbackStart = namedtuple("CallbackStart", ["prototype"])
CallbackEnd = namedtuple("CallbackEnd", [])
CallArgumentsResolve = namedtuple("CallArgumentsResolve", ["method", "arguments"])
CallReturn = namedtuple("CallReturn", ["return_value"])
CallCompleted = namedtuple("CallCompleted", [])
AcceptCallbacks = namedtuple("AcceptCallbacks", ["callbacks"])
IfConditionResolve = namedtuple("IfConditionResolve", ["node"])
SwitchValueResolve = namedtuple("SwitchValueResolve", ["node"])
