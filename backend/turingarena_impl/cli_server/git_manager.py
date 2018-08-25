import os
import logging
import subprocess

from contextlib import contextmanager, ExitStack
from tempfile import TemporaryDirectory

from turingarena_impl.common.git import BASE_GIT_ENV

logger = logging.getLogger(__name__)
git_env = {}


@contextmanager
def setup_git_environment(local, git_dir):
    global git_env

    logger.info("Setting up git")
    with ExitStack() as stack:
        git_temp_dir = stack.enter_context(TemporaryDirectory())
        logger.info(f"Created temporary git working dir {git_temp_dir}")
        if not local:
            git_dir = "/run/turingarena/db.git"
        logger.info(f"Using git repository at {git_dir}")
        git_env = {
            **BASE_GIT_ENV,
            "GIT_DIR": git_dir,
            "GIT_WORK_TREE": git_temp_dir,
        }
        os.chdir(git_temp_dir)
        yield


def git_fetch_repositories(repositories):
    for repository in repositories:
        # TODO: add a way to specify branch and depth
        logger.info(f"Fetching git repository {repository}")
        subprocess.call(["git", "fetch", "--recurse-submodules=yes", repository], env=git_env)


def git_import_trees(tree_ids):
    for tree_id in tree_ids:
        logger.info(f"Importing git tree id {tree_id}")
        subprocess.call(["git", "read-tree", tree_id], env=git_env)
        subprocess.call(["git", "checkout-index", "--all"], env=git_env)


def receive_current_directory(current_dir, tree_id):
    logger.info("Retriving current directory from git")

    git_import_trees([tree_id])

    if current_dir:
        os.chdir(current_dir)


def add_directory(directory):
    logger.info(f"Add directory {directory} to be committed")
    subprocess.call(["git", "add", "-A", directory], env=git_env)


def commit_work():
    logger.info("Committing work")

    tree_id = subprocess.check_output(["git", "write-tree"], env=git_env).strip().decode("ascii")
    logger.info(f"Output written with tree-id {tree_id}")

    commit_id = subprocess.check_output(["git", "commit-tree", tree_id, "-m", "Make output"], env=git_env).strip().decode("ascii")
    logger.info(f"Created commit with commit-id {commit_id}")

    return tree_id, commit_id