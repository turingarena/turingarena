def evaluation_text(evaluation_events):
    return "".join(
        e.payload
        for e in evaluation_events
        if e.type == "text"
    )


def evaluation_goals(evaluation_events):
    return {
        e.payload["goal"]: e.payload["result"]
        for e in evaluation_events
        if e.type == "goal_result"
    }
