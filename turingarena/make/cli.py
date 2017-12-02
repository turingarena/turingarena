import importlib
import json

from turingarena.cli import docopt_cli
from turingarena.make import resolve_plan, make_plan_signature
from turingarena.make.make import sequential_make


@docopt_cli
def make_cli(args):
    """TuringArena task CLI.

    Usage:
      task [options] -m <module> [-n <name>] <cmd> [<args>...]

    Options:

      -m --module=<package>  Python module containing the problem definition
      -n --name=<name>  Qualified name of the problem variable [default: problem]

    """

    plan_module = importlib.import_module(args["--module"])

    print(plan_module)

    plan_descriptor = getattr(plan_module, args["--name"])
    plan = resolve_plan(plan_descriptor.get_tasks())

    commands = {
        "describe": make_describe_cli,
        "run": make_run_cli,
        "compute": make_compute_cli,
        "make": make_make_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](plan=plan, argv=argv2)


@docopt_cli
def make_describe_cli(args, *, plan):
    """TuringArena task describe CLI.

    Usage:
      describe
    """

    print(json.dumps(make_plan_signature(plan), indent=2))


@docopt_cli
def make_compute_cli(args, *, plan):
    """TuringArena task compute CLI.

    Usage:
      compute [options] --phase=<name> [--index=<index>] [--parent=<id>]...

    Options:
      --phase=<name>  Name of the phase to run
      --index=<index>  Index of the specific parametrization of the phase to run
      --parent=<id>  Add a dependency as a Git commit
      --repo-path=<path>  Path to the repository
    """

    phase_name = args["--phase"]
    commit = plan[phase_name].compute(
        repo_path=args["--repo-path"],
        parents=dict([
            p.split(":", 2)
            for p in args["--parent"]
        ]),
    )
    print(commit.hexsha)


@docopt_cli
def make_make_cli(args, *, plan):
    """TuringArena task compute CLI.

    Usage:
      make [options] --phase=<name> [--index=<index>] [--entry=<id>]...

    Options:
      --phase=<name>  Name of the phase to run
      --index=<index>  Index of the specific parametrization of the phase to run
      --entry=<entry>  Add an entry (format: <entry name>:<commit SHA>)
      --repo-path=<path>  Path to the repository
    """

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


@docopt_cli
def make_run_cli(args, *, plan):
    """TuringArena task run CLI.

    Usage:
      run --phase=<name> [--index=<index>]

    Options:
      --phase=<name>  Name of the phase to run
      --index=<index>  Index of the specific parametrization of the phase to run
    """

    phase_name = args["--phase"]
    plan[phase_name].run()
