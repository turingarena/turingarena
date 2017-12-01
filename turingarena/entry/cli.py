"""TuringArena entry CLI.

Usage:
  entry [options] [--parent=<parent>]... --file=<file>...

Options:

  --parent=<parent>  Add a parent commit
  --repo-path=<path>  Path to the repository
  --source-dir=<dir>  Source directory [default: .]
  --file=<file>  Files to add (format: <source>:<dest>)
"""

import importlib

import docopt

from turingarena.entry.files import add_files
from turingarena.make import resolve_plan
from turingarena.make.compute_cli import make_compute_cli
from turingarena.make.describe_cli import make_describe_cli
from turingarena.make.make_cli import make_make_cli
from turingarena.make.run_cli import make_run_cli


def entry_cli(argv):
    args = docopt.docopt(__doc__, argv=argv, options_first=True)

    commit = add_files(
        source_dir=args["--source-dir"],
        repo_path=args["--repo-path"],
        parents=args["--parent"],
        files=[
            f.split(":", 2)
            for f in args["--file"]
        ]
    )
    print(commit.hexsha)
