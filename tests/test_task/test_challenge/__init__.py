from turingarena.problem import Problem

problem = Problem()

@problem.goal
def goal():
    return "goal result"
