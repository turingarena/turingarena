from __future__ import print_function

import os
import subprocess
import sys


def info(*args):
    print(*args, file=sys.stderr)


def turingarena_cli():
    socket_path = "/run/turingarena/sshd.sock"
    ssh_command = (
        [
            "ssh",
            "-q",
            "-o", "ProxyCommand=socat - UNIX-CONNECT:{socket_path}".format(socket_path=socket_path),
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "StrictHostKeyChecking=no",
        ]
    )
    ssh_cli = ssh_command + ["-t", "root@localhost"]

    working_dir = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        universal_newlines=True,
    ).strip()
    current_dir = os.path.relpath(os.curdir, working_dir)
    info("Sending work dir: {working_dir} (current dir: {current_dir})...".format(
        working_dir=working_dir,
        current_dir=current_dir,
    ))

    git_env = {
        "GIT_WORK_TREE": working_dir,
        "GIT_DIR": os.path.join(os.path.expanduser("~"), ".turingarena", "db.git"),
        "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in ssh_command),
    }

    git_popen_args = dict(env=git_env, universal_newlines=True)

    subprocess.check_call(["git", "add", "-A", "."], **git_popen_args)

    tree_id = subprocess.check_output(["git", "write-tree"], **git_popen_args).strip()

    commit_message = "Turingarena payload."
    commit_id = subprocess.check_output(
        ["git", "commit-tree", tree_id, "-m", commit_message],
        **git_popen_args
    ).strip()

    subprocess.check_call(ssh_cli + ["mkdir -p /run/turingarena && git init --bare /run/turingarena/db.git -q"])

    subprocess.check_call([
        "git", "push", "-q",
        "root@localhost:/run/turingarena/db.git",
        "{commit_id}:refs/heads/sha-{commit_id}".format(commit_id=commit_id),
    ], **git_popen_args)

    # remove the remove branch (we only need the tree object)
    subprocess.check_call([
        "git", "push", "-q",
        "root@localhost:/run/turingarena/db.git",
        ":refs/heads/sha-{commit_id}".format(commit_id=commit_id),
    ], **git_popen_args)

    info("Work dir sent. Running command...")

    subprocess.call(ssh_cli + [
        "TURINGARENA_TREE_ID=" + tree_id,
        "TURINGARENA_CURRENT_DIR=" + current_dir,
        "/usr/local/bin/python", "-m", "turingarena_impl",
    ] + sys.argv[1:])


if __name__ == '__main__':
    turingarena_cli()
