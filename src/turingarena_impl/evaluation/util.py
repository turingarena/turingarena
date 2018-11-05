from turingarena_common.evaluation_events import EvaluationEventType


def evaluation_text(evaluation_events):
    return "".join(
        e.payload
        for e in evaluation_events
        if e.type is EvaluationEventType.TEXT
    )
