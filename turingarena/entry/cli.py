from turingarena.cli import docopt_cli

from turingarena.entry.files import add_files


@docopt_cli
def entry_cli(args):
    """TuringArena entry CLI.

    Usage:
      entry [options] [--file=<file>]...

    Options:

      --repo-path=<path>  Path to the repository
      --source-dir=<dir>  Source directory [default: .]
      --file=<file>  Files to add (format: <source>:<dest>)
    """

    commit = add_files(
        source_dir=args["--source-dir"],
        repo_path=args["--repo-path"],
        files=[
            f.split(":", 2)
            for f in args["--file"]
        ]
    )
    print(commit.hexsha)
