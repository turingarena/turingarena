import logging
import subprocess

import git
from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


def compute(command, *, parents, repo_path):
    logger.debug(f"computing command '{command}' with parents: {parents} in repo '{repo_path}'")

    root_repo = git.Repo(path=repo_path)

    with TemporaryDirectory() as temp_dir:
        repo = root_repo.clone(path=temp_dir)

        for parent in parents:
            repo.remote("origin").fetch(parent)
            repo.index.merge_tree(repo.commit(parent))

        repo.index.checkout()

        process = subprocess.run(
            command,
            shell=True,
            cwd=repo.working_dir,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            check=True,
        )

        for line in process.stdout.splitlines():
            logger.debug(f"process output: {line.strip()}")

        repo.index.add("*")

        commit = repo.index.commit(
            f"turingarena compute '{command}'",
            parent_commits=[
                repo.commit(parent)
                for parent in parents
            ],
        )

        repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")
        logger.debug(f"commit message: {commit.message}")
        print(commit.hexsha)
