"""TuringArena task compute CLI.

Usage:
  compute [options] --phase=<name> [--index=<index>] [--parent=<id>]...

Options:
  --phase=<name>  Name of the phase to run
  --index=<index>  Index of the specific parametrization of the phase to run
  --parent=<id>  Add a dependency as a Git commit
  --repo-path=<path>  Path to the repository
"""

import docopt


def make_compute_cli(*, plan, argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)
    phase_name = args["--phase"]
    commit = plan[phase_name].compute(
        repo_path=args["--repo-path"],
        parents=dict([
            p.split(":", 2)
            for p in args["--parent"]
        ]),
    )
    print(commit.hexsha)
