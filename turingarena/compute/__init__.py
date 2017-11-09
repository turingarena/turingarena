import logging
import subprocess

import git
from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


def compute(command, *, parents, repo_path):
    root_repo = git.Repo(path=repo_path)

    with TemporaryDirectory() as temp_dir:
        repo = root_repo.clone(path=temp_dir)

        for parent in parents:
            repo.remote("origin").fetch(parent)
            repo.index.merge_tree(repo.commit(parent))

        repo.index.checkout()

        subprocess.run(
            command,
            shell=True,
            cwd=repo.working_dir,
        )

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
