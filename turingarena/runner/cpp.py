import os
import subprocess


import logging
logger = logging.getLogger(__name__)


def compile_cpp(algorithm_dir, source_file, interface):
    interface_file_name = "generated/interfaces/{}/cpp/main.cpp".format(interface)

    with open(algorithm_dir + "/compilation_output.txt", "w") as compilation_output:
        cli = "g++ -x c++ -o algorithm -"
        logger.debug("Running {}".format(cli))
        compiler = subprocess.Popen(
            cli,
            shell=True,
            cwd=algorithm_dir,
            stdin=subprocess.PIPE,
            stderr=compilation_output,
            universal_newlines=True,
        )

        if interface is not None:
            logger.debug("Streaming interface code")
            print('#line 1 "<interface>"', file=compiler.stdin)
            with open(interface_file_name) as interface_file:
                compiler.stdin.write(interface_file.read())
        logger.debug("Streaming algorithm code")
        print('#line 1 "<algorithm>"', file=compiler.stdin)
        compiler.stdin.write(source_file.read())

        logger.debug("Compiling...")
        compiler.communicate()
        logger.debug("Compiling done.")

        with open(algorithm_dir + "/compilation_return.txt", "w") as compilation_return:
            print(compiler.returncode, file=compilation_return)


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
