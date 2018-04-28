import logging
import os
import subprocess

from turingarena_impl.cli import docopt_cli, init_logger

logger = logging.getLogger(__name__)


def run(*args, **kwargs):
    logger.debug(f"running: {args} {kwargs}")
    return subprocess.run(*args, **kwargs)


@docopt_cli
def turingarena_cli(args):
    """TuringArena command line interface.

    Usage:
      turingarena [options] <cmd> [<args>]...
      turingarena --help-commands

    Options:
      --log-level=<level>
      --socket=<socket>  Connection socket with turingarena [default: /run/turingarena/sshd.sock]
    """

    init_logger(args)

    socket_path = args['--socket']
    ssh_command = (
        [
            "ssh",
            "-q",
            "-o", f"ProxyCommand=socat - UNIX-CONNECT:{socket_path}",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "StrictHostKeyChecking=no",
        ]
    )
    ssh_cli = [*ssh_command, "-t", "root@localhost"]

    working_dir = run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    ).stdout.strip()
    current_dir = os.path.relpath(os.curdir, working_dir)
    logger.info(f"Sending work dir: {working_dir} (current dir: {current_dir})...")

    git_env = {
        "GIT_WORK_TREE": working_dir,
        "GIT_DIR": os.path.join(os.path.expanduser("~"), ".turingarena", "db.git"),
        "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in ssh_command),
    }

    git_popen_args = dict(env=git_env, stdout=subprocess.PIPE, universal_newlines=True)

    run(["git", "add", "-A", "."], **git_popen_args)

    tree_id = run(["git", "write-tree"], **git_popen_args).stdout.strip()

    commit_message = "Turingarena payload."
    commit_id = run(
        ["git", "commit-tree", tree_id],
        input=commit_message,
        **git_popen_args,
    ).stdout.strip()

    run([*ssh_cli, "mkdir -p /run/turingarena && git init --bare /run/turingarena/db.git -q"])

    run([
        "git", "push", "-q",
        "root@localhost:/run/turingarena/db.git",
        f"{commit_id}:refs/heads/sha-{commit_id}",
    ], **git_popen_args)

    # remove the remove branch (we only need the tree object)
    run([
        "git", "push", "-q",
        "root@localhost:/run/turingarena/db.git",
        f":refs/heads/sha-{commit_id}",
    ], **git_popen_args)

    logger.info(f"Work dir sent. Running command...")

    run([
        *ssh_cli,
        f"TURINGARENA_TREE_ID={tree_id}",
        f"TURINGARENA_CURRENT_DIR={current_dir}",
        "/usr/local/bin/python", "-m", "turingarena_impl",
        args["<cmd>"],
        *args["<args>"],
    ])
