from __future__ import print_function

import argparse
import os
import shlex
import subprocess
import sys


def info(message):
    print(message, file=sys.stderr)


def turingarena_daemon():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-dir", type=str, help="source code directory of TuringArena (for development)")

    args = parser.parse_args()

    volumes = []
    if args.dev_dir is not None:
        dev_dir = os.path.abspath(args.dev_dir)
        volumes.append("--mount=type=bind,src={},dst=/usr/local/turingarena/,readonly".format(dev_dir))
    cli = [
              "docker",
              "run",
              "--name=turingarena",
              "--rm",
              "--read-only",
              "--tmpfs=/run/turingarena:exec,mode=1777",
              "--tmpfs=/tmp:exec,mode=1777",
          ] + volumes + [
              "--publish=127.0.0.1:20122:22",
              "turingarena/turingarena",
              "socat",
              "TCP-LISTEN:22,fork",
              """EXEC:"/usr/sbin/sshd -i -e -o PermitEmptyPasswords=yes -o Protocol=2",nofork""",
          ]
    info(str(cli))
    os.execvp("docker", cli)


def turingarena_cli():
    ssh_command = (
        [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "LogLevel=error",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "StrictHostKeyChecking=no",
            "-p", "20122",
        ]
    )

    working_dir = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        universal_newlines=True,
    ).strip()

    current_dir = os.path.relpath(os.curdir, working_dir)
    info("Sending work dir: {working_dir} (current dir: {current_dir})...".format(
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

    info("Work dir sent. Running command...")

    if sys.stdout.isatty():
        tty_allocation = ["-t"]
    else:
        tty_allocation = ["-T"]

    cmd = ssh_command + tty_allocation + [
        "turingarena@localhost",
        "TURINGARENA_TREE_ID=" + tree_id,
        "TURINGARENA_CURRENT_DIR=" + current_dir,
        "/usr/local/bin/python", "-m", "turingarena_impl",
    ] + [shlex.quote(s) for s in sys.argv[1:]]
    subprocess.call(cmd)


if __name__ == '__main__':
    turingarena_cli()
