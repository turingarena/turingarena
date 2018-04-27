import logging
import os
import subprocess

from turingarena_impl.cli import docopt_cli, init_logger

logger = logging.getLogger(__name__)


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
            "-o", f"ProxyCommand=socat - UNIX-CONNECT:{socket_path}",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "StrictHostKeyChecking=no",
        ]
    )
    ssh_cli = [*ssh_command, "root@localhost"]

    working_dir = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    ).stdout
    logger.info(f"Workdir: {working_dir}")

    git_env = {
        "GIT_WORK_TREE": working_dir,
        "GIT_DIR": os.path.join(os.path.expanduser("~"), ".turingarena", "db.git"),
        "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in ssh_command),
    }

    git_popen_args = dict(env=git_env, stdout=subprocess.PIPE, universal_newlines=True)

    subprocess.run(["git", "add", "-A", "."], **git_popen_args)
    tree_id = subprocess.run(["git", "write-tree"], **git_popen_args).stdout
    commit_id = subprocess.run(["git", "commit-tree", tree_id], **git_popen_args).stdout
    subprocess.run(["git", "push", "root@localhost:db.git", f"{commit_id}:sha-{commit_id}"], **git_popen_args)

    subprocess.run([
        *ssh_cli,
        "/usr/local/bin/python", "-m", "turingarena_impl",
        args["<cmd>"],
        *args["<args>"],
    ])


if __name__ == '__main__':
    turingarena_cli()
