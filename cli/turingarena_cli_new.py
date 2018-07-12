from __future__ import print_function

import subprocess
import argparse
import shlex
import json
import uuid
import sys
import os

from termcolor import colored
from tempfile import TemporaryDirectory

ssh_cli = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "LogLevel=error",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "StrictHostKeyChecking=no",
        "-p", "20122", "-q",
]

git_env = {}


def error(string):
    print(colored("==> ERROR:", "red", attrs=["bold"]), string)


def warning(string):
    print(colored("==> WARNING:", "yellow", attrs=["bold"]), string)


def ok(string):
    print(colored("==>", "green", attrs=["bold"]), string)


def info(string):
    print(colored("  ->", "blue", attrs=["bold"]), string)


def build_json_parameters(args):
    return json.dumps(vars(args))


def local_command(args):
    cli = [
        "python3",
        "-m", "turingarena_impl",
        "new_cli",
        build_json_parameters(args),
    ]

    subprocess.call(cli)


def send_ssh_command(cli):
    if sys.stdout.isatty():
        tty_allocation = "-t"
    else:
        tty_allocation = "-T"

    cli = ssh_cli + [
        tty_allocation,
        "turingarena@localhost",
    ] + cli

    ok("Sending command to the server via ssh")
    subprocess.call(cli)


def ssh_command(args):

    cli = [
        "/usr/local/bin/python",
        "-m", "turingarena_impl",
        "new_cli",
        shlex.quote(build_json_parameters(args)),
    ]

    send_ssh_command(cli)


def setup_git_env():
    global git_env

    git_dir = os.path.join(os.path.expanduser("~"), ".turingarena", "db.git")

    try:
        working_dir = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            universal_newlines=True,
        ).strip()
    except:
        working_dir = os.getcwd()
        ok("Initializing git repository in {}".format(working_dir))
        subprocess.call(["git", "init"])

    author_name = "TuringArena"
    author_email = "contact@turingarena.org"

    git_env = {
        "GIT_WORK_TREE": working_dir,
        "GIT_DIR": git_dir,
        "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in ssh_cli),
        "GIT_AUTHOR_NAME": author_name,
        "GIT_AUTHOR_EMAIL": author_email,
        "GIT_COMMITTER_NAME": author_name,
        "GIT_COMMITTER_EMAIL": author_email,
    }

    subprocess.check_call(["git", "init", "--quiet", "--bare", git_dir])
    info("Initialized git repository in {}".format(git_dir))

    return git_dir


def send_current_dir(local):
    global git_env
    working_dir = git_env["GIT_WORK_TREE"]

    current_dir = os.path.relpath(os.curdir, working_dir)
    ok("Sending work dir: {working_dir} (current dir: {current_dir})...".format(
        working_dir=working_dir,
        current_dir=current_dir,
    ))

    git_popen_args = dict(env=git_env, universal_newlines=True)

    subprocess.check_call(["git", "add", "-A", "."], **git_popen_args)
    info("Added all files to git")

    tree_id = subprocess.check_output(["git", "write-tree"], **git_popen_args).strip()
    info("Wrote tree with id {}".format(tree_id))

    if not local:
        ok("Sending current directory to the server via git")

        commit_message = "Turingarena payload."
        commit_id = subprocess.check_output(
            ["git", "commit-tree", tree_id, "-m", commit_message],
            **git_popen_args
        ).strip()

        info("Created commit {}".format(commit_id))

        subprocess.check_call(ssh_cli + [
            "turingarena@localhost",
            "git init --bare --quiet db.git",
        ])
        info("Initialized git repository on the server")

        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            "{commit_id}:refs/heads/sha-{commit_id}".format(commit_id=commit_id),
        ], **git_popen_args)
        info("Pushed current commit")

        # remove the remove branch (we only need the tree object)
        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            ":refs/heads/sha-{commit_id}".format(commit_id=commit_id),
        ], **git_popen_args)

    return current_dir, tree_id


def retrive_result(result_file):
    ok("Retriving result")
    info("Reading {}".format(result_file))
    with open(result_file) as f:
        result = f.read().strip()

    info("Got {}".format(result))
    result = json.loads(result)

    tree_id = result["tree_id"]
    commid_it = result["commit_id"]

    info("Importing tree id {}".format(tree_id))
    subprocess.call(["git", "read-tree", tree_id], env=git_env)
    info("Checking out")
    subprocess.call(["git", "checkout-index", "--all", "-q"], env=git_env)


def create_evaluate_parser(evaluate_parser):
    evaluate_parser.add_argument("file", help="submission file", nargs="+")
    evaluate_parser.add_argument("--evaluator", "-e", help="command evaluator")
    evaluate_parser.add_argument("--raw", "-r", help="use raw output", action="store_true")


def create_make_parser(make_parser):
    make_parser.add_argument("what", help="what to make", default="all", choices=["all", "skeleton", "template", "metadata"], nargs="?")
    make_parser.add_argument("--language", "-l", help="which language to generate", action="append")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Turingarena CLI")
    parser.add_argument("--local", "-l", help="execute turingarena locally (do not connect to docker)", action="store_true")
    parser.add_argument("--send-current-dir", "-s", help="send the current directory", action="store_true")
    parser.add_argument("--tree", "-t", help="a git tree id", action="append")
    parser.add_argument("--repository", "-r", help="source of a git repository", action="append")

    subparsers = parser.add_subparsers(title="command", dest="command")
    subparsers.required = True

    make_parser = subparsers.add_parser("make", help="Generate all the necessary files for a problem")
    create_make_parser(make_parser)

    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate a submission")
    create_evaluate_parser(evaluate_parser)

    return parser.parse_args()


def turingarena_cli():
    args = parse_arguments()

    args.git_dir = setup_git_env()

    if args.send_current_dir:
        args.current_dir, args.tree_id = send_current_dir(local=args.local)

    args.result_file = os.path.join("/tmp", "turingarena_{}_result.json".format(str(uuid.uuid4())))

    if args.local:
        local_command(args)
    else:
        ssh_command(args)

    retrive_result(args.result_file)


if __name__ == "__main__":
    turingarena_cli()
