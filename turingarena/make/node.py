import logging
import multiprocessing
import os
from tempfile import TemporaryDirectory

import git

from turingarena.common import ImmutableObject

logger = logging.getLogger(__name__)


class EvaluationNode(ImmutableObject):
    __slots__ = ["name"]


class EvaluationEntry(EvaluationNode):
    __slots__ = []

    def create(*, source_dir, files, repo_path):
        root_repo = git.Repo(path=repo_path)

        with TemporaryDirectory() as temp_dir:
            repo = root_repo.clone(path=temp_dir)

            repo.index.checkout()

            for src, dest in files:
                shutil.copy(
                    os.path.join(source_dir, src),
                    os.path.join(temp_dir, dest),
                )

            repo.index.add("*")

            files = ", ".join(dest for src, dest in files)
            commit = repo.index.commit(
                f"entry with files {files}",
            )

            repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")
            logger.debug(f"commit message: {commit.message}")

            return commit


class EvaluationTask(EvaluationNode):
    __slots__ = ["dependencies", "target"]

    def run(self):
        self.target()

    def compute(self, *, parents, repo_path):
        logger.debug(f"running task '{self}' with parents: {parents} in repo '{repo_path}'")

        assert set(parents.keys()) == set(d.name for d in self.dependencies)
        assert all(isinstance(p, str) for p in parents.values())

        root_repo = git.Repo(path=repo_path)

        with TemporaryDirectory() as temp_dir:
            repo = root_repo.clone(path=temp_dir)

            for parent in parents.values():
                repo.remote("origin").fetch(parent)
                repo.index.merge_tree(repo.commit(parent))

            repo.index.checkout()

            def target():
                os.chdir(repo.working_dir)
                self.run()

            process = multiprocessing.Process(
                target=target,
            )
            process.start()
            process.join()
            if process.exitcode:
                raise RuntimeError(f"task failed (error code {process.exitcode})")

            repo.index.add("*")

            commit = repo.index.commit(
                f"turingarena compute '{self.name}'",
                parent_commits=[
                    repo.commit(parent)
                    for parent in parents.values()
                ],
            )

            repo.remote("origin").push(f"{commit}:refs/heads/sha-{commit}")
            logger.debug(f"commit message: {commit.message}")

            return commit