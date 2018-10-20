import json
import logging
import os
import subprocess
from argparse import ArgumentParser
from contextlib import contextmanager
from functools import lru_cache
from tempfile import TemporaryDirectory

from turingarena_cli.remote import AbstractRemotePythonCommand, RemotePythonCommand
from turingarena_cli.ssh import SSH_BASE_CLI
from turingarena_common.commands import WorkingDirectory, Pack, GitCloneRepository
from turingarena_common.git_common import GIT_BASE_ENV


class PackBasedCommand(AbstractRemotePythonCommand):
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
    def local_tree_id(self, path):
        logging.info("Packing local tree")
        with self._temp_git_index(work_dir=path) as env:
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
    def working_dir_tree_id(self):
        return self.local_tree_id(self.git_work_dir)

    @property
    @lru_cache(None)
    def relative_current_dir(self):
        if self.args.current_dir is not None:
            return self.args.current_dir

        if self.send_working_dir:
            current_dir = os.path.relpath(self.cwd, self.git_work_dir)
            logging.info("Relative current dir: {current_dir}".format(current_dir=current_dir))
            return current_dir
        else:
            return "."

    def push_local_tree(self, tree_id):
        logging.info("Pushing tree {tree_id}...".format(tree_id=tree_id))
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

    @property
    def send_working_dir(self):
        if self.args.send_working_dir == "always":
            return True
        if self.args.send_working_dir == "auto":
            return self.args.local_dir is None and self.args.tree is None
        if self.args.send_working_dir == "never":
            return False
        raise AssertionError

    @property
    @lru_cache(None)
    def local_parts(self):
        parts = []

        local_dirs = self.args.local_dir or []
        for d in local_dirs:
            parts.append(self.local_tree_id(d))

        if self.send_working_dir:
            parts += [self.working_dir_tree_id]

        return parts

    @property
    @lru_cache(None)
    def parts(self):
        parts = self.args.tree or []
        parts.extend(self.local_parts)

        return parts

    @property
    def working_directory(self):
        return WorkingDirectory(
            pack=Pack(
                parts=self.parts,
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

    def run(self):
        self.git_init()
        for p in self.local_parts:
            self.push_local_tree(p)
        return super(PackBasedCommand, self).run()

    PARSER = ArgumentParser(
        add_help=False,
        parents=[RemotePythonCommand.PARSER],
    )

    PARSER.add_argument(
        "--send-working-dir",
        choices=["never", "always", "auto"],
        default="auto",
        help="specifies whether to send the current working dir to the problem pack",
    )
    PARSER.add_argument(
        "--local-dir",
        action="append",
        help="add a local directory to the problem pack",
    )
    PARSER.add_argument(
        "--tree",
        action="append",
        help="add a git tree to the problem pack",
    )
    PARSER.add_argument(
        "--repository",
        action="append",
        help="source of a git repository",
    )

    PARSER.add_argument(
        "--current-dir",
        help="",
    )
