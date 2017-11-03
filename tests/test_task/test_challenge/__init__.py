from turingarena.problem import Problem

problem = Problem()

problem.implementation_submission_item(
    "solution",
    protocol_name="test_challenge",
    interface_name="exampleinterface",
)

@problem.goal
def goal(solution):
    return f"goal (solution: {solution})"
