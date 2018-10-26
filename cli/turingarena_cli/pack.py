import logging
import os
import subprocess

from argparse import ArgumentParser
from contextlib import contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena_cli.remote import AbstractRemotePythonCommand, RemotePythonCommand
from turingarena_cli.ssh import SSH_BASE_CLI
from turingarena_common.commands import WorkingDirectory, Pack
from turingarena_common.git_common import GIT_BASE_ENV


class PackBasedCommand(AbstractRemotePythonCommand):
    @property
    def git_env(self):
        git_env = {
            "GIT_DIR": self.git_dir,
            "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in SSH_BASE_CLI),
        }
        git_env.update(GIT_BASE_ENV)
        return git_env

    def git_init(self):
        subprocess.check_call(["git", "init", "--quiet", "--bare", self.git_dir])
        logging.info("Initialized git repository in {}".format(self.git_dir))

    @contextmanager
    def _temp_git_index(self, work_dir=None):
        with TemporaryDirectory() as temp_dir:
            env = {}
            env.update(self.git_env)
            env.update({
                "GIT_INDEX_FILE": os.path.join(temp_dir, "index")
            })
            if work_dir is not None:
                env.update({
                    "GIT_WORK_TREE": work_dir,
                })
            yield env

    @lru_cache(None)
    def local_oid(self, path):
        logging.info("Packing local tree")
        with self._temp_git_index(work_dir=path) as env:
            subprocess.check_call(["git", "add", "-A", "."], env=env)
            logging.info("Added all files to git")

            tree_oid = subprocess.check_output(
                ["git", "write-tree"],
                env=env,
                universal_newlines=True,
            ).strip()
            logging.info("Wrote tree with id {}".format(tree_oid))

            commit_message = "Turingarena local directory: {path}.".format(path=path)

            oid = subprocess.check_output(
                ["git", "commit-tree", tree_oid, "-m", commit_message],
                env=self.git_env,
                universal_newlines=True,
            ).strip()
            logging.info("Created commit {}".format(oid))

            return oid

    @property
    def working_dir(self):
        return self.args.working_dir if self.args.working_dir else "."

    @property
    @lru_cache(None)
    def working_dir_oid(self):
        return self.local_oid(self.working_dir)

    @property
    def relative_current_dir(self):
        return self.args.current_dir if self.args.current_dir else "."

    def push_local_commit(self, oid):
        logging.info("Pushing commit {oid}...".format(oid=oid))

        subprocess.check_call(SSH_BASE_CLI + [
            "turingarena@localhost",
            "git init --bare --quiet db.git",
        ])
        logging.info("Initialized git repository on the server")

        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            "{oid}:refs/heads/sha-{oid}".format(oid=oid),
        ], env=self.git_env)
        logging.info("Pushed current commit")

        # remove the remove branch (we only need the tree object)
        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            ":refs/heads/sha-{oid}".format(oid=oid),
        ], env=self.git_env)

    @property
    def working_directory(self):
        return WorkingDirectory(
            pack=Pack(
                oid=self.working_dir_oid,
                repository=None,
            ),
            current_directory=self.relative_current_dir,
        )

    def run(self):
        self.git_init()
        self.push_local_commit(self.working_dir_oid)
        return super(PackBasedCommand, self).run()

    PARSER = ArgumentParser(
        add_help=False,
        parents=[RemotePythonCommand.PARSER],
    )

    PARSER.add_argument(
        "--working-dir",
        action="append",
    )
    PARSER.add_argument(
        "--current-dir",
        help="",
    )
