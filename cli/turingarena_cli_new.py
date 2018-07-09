#!/usr/bin/env python

from __future__ import print_function

import subprocess
import argparse
import shlex
import json
import sys
import os

ssh_command = [
    "ssh",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=error",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "StrictHostKeyChecking=no",
    "-p", "20122",
]


def build_json_parameters(args):
    json_data = {}

    json_data["command"] = args.command

    json_data["trees"] = [
        tree
        for tree in args.tree
    ]

    json_data["repositories"] = [
        repository
        for repository in args.repository
    ] if args.repository else []

    json_data["submitted_files"] = [
        file
        for file in args.file
    ] if args.file else []

    return json.dumps(json_data)


def send_ssh_command(args):
    if sys.stdout.isatty():
        tty_allocation = ["-t"]
    else:
        tty_allocation = ["-T"]

    cli = ssh_command + tty_allocation + ["turingarena@localhost"]

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

    subprocess.call(cli)


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
        "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in ssh_command),
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

    subprocess.check_call(ssh_command + [
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


def parse_arguments():
    parser = argparse.ArgumentParser(description="Turingarena CLI")
    parser.add_argument("command", help="the command", choices=["evaluate", "make"])
    parser.add_argument("tree", help="a git tree id", nargs="*")
    parser.add_argument("--repository", "-r", help="source of a git repository", action="append")
    parser.add_argument("--send-current-dir", "-s", help="send the current directory", action="store_true")
    parser.add_argument("--file", "-f", help="submission file", action="append")

    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        send_ssh_command(args)
    except subprocess.CalledProcessError:
        print("Error connecting to turingarena daemon. Is it running ?")


if __name__ == "__main__":
    main()