"""TuringArena problem CLI.

Usage:
  goal [options] (task|evaluate) [<args>...]

Options:
  -n --name=<name>  Name of the goal [default: goal].

"""

import docopt


def problem_goal_cli(*, problem_id, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    problem = problem_id.load()

    name = args["--name"]
    goal = problem.goals[name]

    argv2 = args["<args>"]

    if args["task"]: return print(goal.to_task_description(problem_id).to_json())
