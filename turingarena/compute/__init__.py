import logging
import subprocess

import git
from tempfile import TemporaryDirectory

logger = logging.getLogger(__name__)


def compute(command, *, deps, repo_path):
    root_repo = git.Repo(path=repo_path)

    with TemporaryDirectory() as temp_dir:
        repo = root_repo.clone(path=temp_dir)

        for dep in deps:
            repo.remote("origin").fetch(dep)
            repo.index.merge_tree(repo.commit(dep))

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
                repo.commit(dep)
                for dep in deps
            ],
        )

        repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")
        logger.debug(f"commit message: {commit.message}")
        print(commit.hexsha)
