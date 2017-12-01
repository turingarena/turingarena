"""TuringArena task compute CLI.

Usage:
  make [options] --phase=<name> [--index=<index>] [--entry=<id>]...

Options:
  --phase=<name>  Name of the phase to run
  --index=<index>  Index of the specific parametrization of the phase to run
  --entry=<entry>  Add an entry (format: <entry name>:<commit SHA>)
  --repo-path=<path>  Path to the repository
"""

import docopt

from turingarena.make.make import sequential_make


def make_make_cli(*, plan, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    commit_sha = sequential_make(
        plan=plan,
        task_name=args["--phase"],
        repo_path=args["--repo-path"],
        entries=dict([
            e.split(":", 2)
            for e in args["--entry"]
        ])
    )
    print(commit_sha)
