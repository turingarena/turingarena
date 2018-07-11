from __future__ import print_function

import subprocess
import argparse
import shlex
import json
import sys
import os


ssh_cli = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "LogLevel=error",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "StrictHostKeyChecking=no",
        "-p", "20122",
]


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

    subprocess.call(cli)


def ssh_command(args):

    cli = []

    if args.send_current_dir:
        current_dir, tree_id = send_current_dir()
        cli += [
            "TURINGARENA_TREE_ID=" + tree_id,
            "TURINGARENA_CURRENT_DIR=" + current_dir,
        ]

    cli += [
        "/usr/local/bin/python",
        "-m", "turingarena_impl",
        "new_cli",
        shlex.quote(build_json_parameters(args)),
    ]

    send_ssh_command(cli)


def send_current_dir():
    working_dir = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        universal_newlines=True,
    ).strip()

    current_dir = os.path.relpath(os.curdir, working_dir)
    print("Sending work dir: {working_dir} (current dir: {current_dir})...".format(
        working_dir=working_dir,
        current_dir=current_dir,
    ))

    git_dir = os.path.join(os.path.expanduser("~"), ".turingarena", "db.git")
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

    git_popen_args = dict(env=git_env, universal_newlines=True)

    subprocess.check_call(["git", "init", "--quiet", "--bare", git_dir])
    subprocess.check_call(["git", "add", "-A", "."], **git_popen_args)

    tree_id = subprocess.check_output(["git", "write-tree"], **git_popen_args).strip()

    commit_message = "Turingarena payload."
    commit_id = subprocess.check_output(
        ["git", "commit-tree", tree_id, "-m", commit_message],
        **git_popen_args
    ).strip()

    subprocess.check_call(ssh_cli + [
        "turingarena@localhost",
        "git init --bare --quiet db.git",
    ])


    subprocess.check_call([
        "git", "push", "-q",
        "turingarena@localhost:db.git",
        "{commit_id}:refs/heads/sha-{commit_id}".format(commit_id=commit_id),
    ], **git_popen_args)

    # remove the remove branch (we only need the tree object)
    subprocess.check_call([
        "git", "push", "-q",
        "turingarena@localhost:db.git",
        ":refs/heads/sha-{commit_id}".format(commit_id=commit_id),
    ], **git_popen_args)

    return current_dir, tree_id


def create_evaluate_parser(evaluate_parser):
    evaluate_parser.add_argument("file", help="submission file", nargs="+")
    evaluate_parser.add_argument("--evaluator", "-e", help="command evaluator")
    evaluate_parser.add_argument("--raw", "-r", help="use raw output", action="store_true")


def create_make_parser(make_parser):
    make_parser.add_argument("what", help="what to make", default="all", choices=["all", "skeleton", "template", "metadata"], nargs="?")
    make_parser.add_argument("--language", "-l", help="wich language to generate", action="append")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Turingarena CLI")
    parser.add_argument("--local", "-l", help="execute turingarena locally (do not connect to docker)", action="store_true")
    parser.add_argument("--send-current-dir", "-s", help="send the current directory", action="store_true")
    parser.add_argument("--tree", "-t", help="a git tree id", nargs="*")
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

    if args.local:
        local_command(args)
    else:
        ssh_command(args)


if __name__ == "__main__":
    turingarena_cli()
