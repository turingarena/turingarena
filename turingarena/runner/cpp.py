import os
import subprocess


class CompilationFailed(Exception):
    pass


def compile_cpp(algorithm_dir, source_file, interface):
    interface_file_name = "generated/interfaces/{}/cpp/main.cpp".format(interface)
    compiler = subprocess.Popen(
        "g++ -x c++ -o algorithm -",
        shell=True,
        cwd=algorithm_dir,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    print('#line 1 "<interface>"', file=compiler.stdin)
    with open(interface_file_name) as interface_file:
        compiler.stdin.write(interface_file.read())
    print('#line 1 "<algorithm>"', file=compiler.stdin)
    compiler.stdin.write(source_file.read())
    _, errors = compiler.communicate()
    if compiler.returncode:
        raise CompilationFailed(errors)
