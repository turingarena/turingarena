import sys

from turingarena.problem import Problem
from turingarena.sandbox.compile import sandbox_compile
from turingarena.task import task

problem = Problem()

problem.implementation_entry(
    "entry",
    protocol_name="test_challenge",
    interface_name="exampleinterface",
)


@problem.goal
def goal(entry):
    N = 10
    M = 100
    A = [i * i for i in range(N)]
    with entry.run(N=N, M=M, A=A) as p:
        S = p.solve(3, test=lambda a, b: a + b)

    print("Answer:", S, file=sys.stderr)


@task()
def compile():
    sandbox_compile(
        source_filename="entry.cpp",
        protocol_name="test_challenge",
        interface_name="exampleinterface",
        algorithm_name="entry",
    )


@task(compile)
def main_task():
    pass
