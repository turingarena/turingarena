import logging
import os
import shutil
from tempfile import TemporaryDirectory

import git

logger = logging.getLogger(__name__)


def add_files(*, source_dir, parents, files, repo_path):
    root_repo = git.Repo(path=repo_path)

    with TemporaryDirectory() as temp_dir:
        repo = root_repo.clone(path=temp_dir)

        for parent in parents:
            repo.remote("origin").fetch(parent)
            repo.index.merge_tree(repo.commit(parent))

        repo.index.checkout()

        for src, dest in files:
            shutil.copy(
                os.path.join(source_dir, src),
                os.path.join(temp_dir, dest),
            )

        repo.index.add("*")

        files = ", ".join(f[1] for f in files)
        commit = repo.index.commit(
            f"added files {files}",
            parent_commits=[
                repo.commit(parent)
                for parent in parents
            ],
        )

        repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")
        logger.debug(f"commit message: {commit.message}")

        return commit
