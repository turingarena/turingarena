from collections.__init__ import namedtuple

Step = namedtuple("Step", ["direction", "body"])
CallbackStart = namedtuple("CallbackStart", ["prototype"])
CallbackEnd = namedtuple("CallbackEnd", [])
CallArgumentsResolve = namedtuple("CallArgumentsResolve", ["method", "arguments"])
CallReturn = namedtuple("CallReturn", ["return_value"])
CallCompleted = namedtuple("CallCompleted", [])
AcceptCallbacks = namedtuple("AcceptCallbacks", ["callbacks"])
IfConditionResolve = namedtuple("IfConditionResolve", ["node"])
SwitchValueResolve = namedtuple("SwitchValueResolve", ["node"])