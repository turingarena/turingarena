"""TuringArena problem CLI.

Usage:
  entry [options] compile task [<args>...]

Options:
  -n --name=<name>  Name of the entry [default: entry].

"""

import docopt


def problem_entry_cli(*, problem_id, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    problem = problem_id.load()

    name = args["--name"]
    entry = problem.entries[name]

    argv2 = args["<args>"]
    if args["compile"] and args["task"]:
        print(entry.compile_task_description().to_json())
