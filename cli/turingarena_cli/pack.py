import json
import logging
import os
import subprocess
from argparse import ArgumentParser
from contextlib import contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena_cli.ssh import SSH_BASE_CLI
from turingarena_cli.remote import AbstractRemoteCommand
from turingarena_common.commands import WorkingDirectory, Pack, GitCloneRepository
from turingarena_common.git_common import GIT_BASE_ENV


class PackBasedCommand(AbstractRemoteCommand):
    @property
    @lru_cache(None)
    def git_work_dir(self):
        try:
            work_dir = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                universal_newlines=True,
            ).strip()
        except:
            work_dir = self.cwd
            logging.info("Initializing git repository in {}".format(work_dir))
            subprocess.call(["git", "init"])
        logging.info("Work dir: {work_dir}".format(work_dir=work_dir))
        return work_dir

    @property
    def git_env(self):
        git_env = {
            "GIT_WORK_TREE": self.git_work_dir,
            "GIT_DIR": self.git_dir,
            "GIT_SSH_COMMAND": " ".join("'" + c + "'" for c in SSH_BASE_CLI),
        }
        git_env.update(GIT_BASE_ENV)
        return git_env

    def git_init(self):
        subprocess.check_call(["git", "init", "--quiet", "--bare", self.git_dir])
        logging.info("Initialized git repository in {}".format(self.git_dir))

    @contextmanager
    def _temp_git_index(self):
        with TemporaryDirectory() as temp_dir:
            env = {}
            env.update(self.git_env)
            env.update({
                "GIT_INDEX_FILE": os.path.join(temp_dir, "index")
            })
            yield env

    @property
    @lru_cache(None)
    def local_tree_id(self):
        logging.info("Packing local tree")
        with self._temp_git_index() as env:
            subprocess.check_call(["git", "add", "-A", "."], env=env)
            logging.info("Added all files to git")

            tree_id = subprocess.check_output(
                ["git", "write-tree"],
                env=env,
                universal_newlines=True,
            ).strip()
            logging.info("Wrote tree with id {}".format(tree_id))
            return tree_id

    @property
    @lru_cache(None)
    def relative_current_dir(self):
        current_dir = os.path.relpath(self.cwd, self.git_work_dir)
        logging.info("Relative current dir: {current_dir}".format(current_dir=current_dir))
        return current_dir

    def push_local_tree(self, tree_id):
        logging.info("Sending current directory to the server via git")
        commit_message = "Turingarena payload."

        commit_id = subprocess.check_output(
            ["git", "commit-tree", tree_id, "-m", commit_message],
            env=self.git_env,
            universal_newlines=True,
        ).strip()
        logging.info("Created commit {}".format(commit_id))

        subprocess.check_call(SSH_BASE_CLI + [
            "turingarena@localhost",
            "git init --bare --quiet db.git",
        ])
        logging.info("Initialized git repository on the server")

        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            "{commit_id}:refs/heads/sha-{commit_id}".format(commit_id=commit_id),
        ], env=self.git_env)
        logging.info("Pushed current commit")

        # remove the remove branch (we only need the tree object)
        subprocess.check_call([
            "git", "push", "-q",
            "turingarena@localhost:db.git",
            ":refs/heads/sha-{commit_id}".format(commit_id=commit_id),
        ], env=self.git_env)

    def retrieve_result(self, result_file):
        logging.info("Retrieving result")
        logging.info("Reading {}".format(result_file))
        with open(result_file) as f:
            result = f.read().strip()

        logging.info("Got {}".format(result))
        result = json.loads(result)

        tree_id = result["tree_id"]
        commit_it = result["commit_id"]

        logging.info("Importing tree id {}".format(tree_id))
        subprocess.call(["git", "read-tree", tree_id], env=self.git_env)
        logging.info("Checking out")
        subprocess.call(["git", "checkout-index", "--all", "-q"], env=self.git_env)

    @property
    def working_directory(self):
        parts = []
        if self.args.send_current_dir:
            parts += [self.local_tree_id]

        return WorkingDirectory(
            pack=Pack(
                parts=parts,
                repositories=[
                    GitCloneRepository(
                        url=url,
                        branch=None,
                        depth=None,
                    )
                    for url in self.args.repository or []
                ],
            ),
            current_directory=self.relative_current_dir,
        )


    PARSER = ArgumentParser(add_help=False)

    PARSER.add_argument(
        "--send-current-dir", "-s",
        action="store_true",
        help="send the current directory",
    )
    PARSER.add_argument(
        "--tree", "-t",
        action="append",
        help="a git tree id",
    )
    PARSER.add_argument(
        "--repository", "-r",
        action="append",
        help="source of a git repository",
    )
