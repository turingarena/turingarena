import logging
import subprocess

import os
import pkg_resources
import shutil

from turingarena.setup.common import module_to_python_package, PROTOCOL_QUALIFIER

logger = logging.getLogger(__name__)


def compile_cpp(algorithm_dir, source_filename, protocol_name, interface_name, check):
    skeleton_path = pkg_resources.resource_filename(
        module_to_python_package(PROTOCOL_QUALIFIER, protocol_name),
        f"_skeletons/{interface_name}/cpp/main.cpp",
    )

    shutil.copy(source_filename, os.path.join(algorithm_dir, "source.cpp"))
    shutil.copy(skeleton_path, os.path.join(algorithm_dir, "skeleton.cpp"))

    cli = [
        "g++",
        "-o", "algorithm",
        "source.cpp",
        "skeleton.cpp",
    ]
    logger.debug(f"Running {' '.join(cli)}")

    with open(algorithm_dir + "/compilation_output.txt", "w") as compilation_output:
        compiler = subprocess.run(
            cli,
            cwd=algorithm_dir,
            stderr=compilation_output,
            universal_newlines=True,
        )

    with open(algorithm_dir + "/compilation_return.txt", "w") as compilation_return:
        print(compiler.returncode, file=compilation_return)

    if compiler.returncode != 0:
        logger.warning("Compilation failed")
        if check:
            raise ValueError("Compilation failed")
