from collections import namedtuple


class EvaluateRequest(namedtuple("ApiSubmission", ["submission", "packs", "repositories"])):
    pass


class EvaluationPage(namedtuple("EvaluationPage", ["begin", "end", "data"])):
    pass
