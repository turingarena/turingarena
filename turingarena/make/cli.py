import json

from turingarena.cli import docopt_cli
from turingarena.make.make import sequential_make
from turingarena.make.node import make_plan_signature, load_plan


@docopt_cli
def make_cli(args):
    """TuringArena make CLI.

    Usage:
      make [options] <cmd> [<args>...]
    """

    # FIXME: reuse common option '--plan'

    commands = {
        "describe": make_describe_cli,
        "run": make_run_cli,
        "compute": make_compute_cli,
        "make": make_make_cli,
    }
    argv2 = args["<args>"]
    return commands[args["<cmd>"]](argv=argv2)


@docopt_cli
def make_describe_cli(args):
    """TuringArena task describe CLI.

    Usage:
      describe <plan>
    """

    plan = load_plan(args["<plan>"])
    print(json.dumps(make_plan_signature(plan), indent=2))


@docopt_cli
def make_compute_cli(args):
    """TuringArena task compute CLI.

    Usage:
      compute <task> [--parent=<id>]...

    Options:
      --plan=<plan>  Name of the plan containing the task
      <task>  Name of the task to compute
      --parent=<id>  Add a dependency as a Git commit
      --repo-path=<path>  Path to the repository
    """

    task_name = args["<task>"]
    plan = load_plan(args["--plan"] or task_name)
    task = plan[task_name]
    commit = task.compute(
        repo_path=args["--repo-path"],
        parents=dict([
            p.split(":", 2)
            for p in args["--parent"]
        ]),
    )
    print(commit.hexsha)


@docopt_cli
def make_make_cli(args):
    """TuringArena task compute CLI.

    Usage:
      make [options] <task> [--entry=<id>]...

    Options:
      --plan=<plan>  Name of the plan containing the task
      <task>  Name of the task to make
      --entry=<entry>  Add an entry (format: <entry name>:<commit SHA>)
      --repo-path=<path>  Path to the repository
    """

    task_name = args["<task>"]
    plan = load_plan(args["--plan"] or task_name)
    commit_sha = sequential_make(
        plan=plan,
        task_name=task_name,
        repo_path=args["--repo-path"],
        entries=dict([
            e.split(":", 2)
            for e in args["--entry"]
        ])
    )
    print(commit_sha)


@docopt_cli
def make_run_cli(args):
    """TuringArena task run CLI.

    Usage:
      run <task> [--index=<index>]

    Options:
      <task>  Name of the task to run
      --plan=<plan>  Name of the plan containing the task
    """

    task_name = args["<task>"]
    plan = load_plan(args["--plan"] or task_name)
    task = plan[task_name]
    task.run()
