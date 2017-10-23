import subprocess

from turingarena.sandbox.compile.cpp import logger


def run_cpp(algorithm_dir, downward_pipe, upward_pipe):
    with open(algorithm_dir + "compilation_return.txt") as f:
        compilation_return = int(f.read().strip())

    if compilation_return:
        return None

    logger.debug("Starting process")
    return subprocess.Popen(
        [algorithm_dir + "algorithm"],
        universal_newlines=True,
        stdin=downward_pipe,
        stdout=upward_pipe,
        bufsize=1
    )