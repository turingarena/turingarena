import logging

from turingarena.make.node import EvaluationEntry, Task

logger = logging.getLogger(__name__)


def sequential_make(*, plan, task_name, repo_path, entries):
    cache = {n: None for n in plan}

    def dfs(node):
        logger.debug(f"computing node {node} (cache: {cache})")

        if isinstance(node, Task):
            for d in node.dependencies:
                cached = cache[d.name]
                logger.debug(f"resolving dependency {d} (cached: {cached})")
                if cached is None:
                    logger.debug(f"cache miss")
                    dfs(d)

            commit = node.compute(
                parents={
                    d.name: cache[d.name]
                    for d in node.dependencies
                },
                repo_path=repo_path,
            )
            cache[node.name] = commit.hexsha
        elif isinstance(node, EvaluationEntry):
            cache[node.name] = entries[node.name]
        else:
            raise AssertionError

    dfs(plan[task_name])

    return cache[task_name]
