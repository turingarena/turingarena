from collections import namedtuple

from turingarena_impl.api.handler import EvaluateRequest


class HyperShEvaluateHandler(namedtuple("HyperShEvaluateHandler", [
    "func_name", "func_uuid",
])):
    def evaluate(self, request: EvaluateRequest) -> str:
        """
        Start the evaluation of a submission,
        by launching an Hyper.sh Func.
        """
        # TODO
