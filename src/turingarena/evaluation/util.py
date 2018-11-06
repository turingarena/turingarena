from turingarena.evaluation.events import EvaluationEventType


def evaluation_text(evaluation_events):
    return "".join(
        e.payload
        for e in evaluation_events
        if e.type is EvaluationEventType.TEXT
    )


def evaluation_goals(evaluation_events):
    return {
        e.payload["goal"]: e.payload["result"]
        for e in evaluation_events
        if e.type is EvaluationEventType.DATA
        if e.payload["type"] == "goal_result"
    }
