"""Task Wizard.

Usage:
  taskwizard create <name> [<folder>]
  taskwizard generate [options]
  taskwizard run [options] [-a <algorithm>]... <executable> [<args>...]
  taskwizard cpp module flags
  taskwizard verify [options]
  taskwizard evaluate [options] [-t <test case>] [-p <phase>] [-l <language>]... [<file>]...
  taskwizard summary [options] [-t <test case>] [-p <phase>]
  taskwizard (-h | --help)

Commands:

  create  Creates a new task definition folder
  generate  Generate all the code

  run  Runs a module

  cpp module flags  Gets the flags to compile a module with GCC

  verify  Verify this problem

  evaluate  Evaluate this problem on some submissions
  summary  Summarize the result of an evaluation

Global options:

  -h --help  Show this screen

  -d --definition-dir=<dir>  Task definition directory [default: .]
  -i --input-dir=<dir>  Input directory [default: .task/]
  -o --output-dir=<dir>  Output directory [default: .task/]

  -v --verbose  Be verbose

Run options:

  -a --algorithm=<algorithm>  Expose an executable as an algorithm to the module.
      Use syntax <slot>:<executable> for <algorithm>

Test options:

  -t --test-case=<test case>  The test case to consider.
  -p --test-phase=<phase>  The test phase to consider.

  If the test case is omitted, then all test cases are considered.
  If a phase is specified but it is not defined in a given test case,
  then the test case is not considered.

  Example:
      taskwizard evaluate -p generate_input
  evaluates the phase 'generate_input' for every test case
  which defines a phase called 'generate_input',

Command evaluate options:

  <file>  Submission file. Use the syntax <slot>=<file> to specify a slot.
  -l --language=<language>  Programming language. Use the syntax -l <slot>=<language> to specify a slot.

"""
import os

import coloredlogs
import docopt
import pkg_resources
import logging

from taskwizard.definition import grammar
from taskwizard.generator import CodeGenerator
from taskwizard.parser import TaskParser
from taskwizard.runner import ModuleRunner


def main():
    args = docopt.docopt(__doc__)

    definition_dir = args["--definition-dir"]
    input_dir = args["--input-dir"]
    output_dir = args["--output-dir"]

    level = logging.WARNING
    if args["--verbose"]:
        level = logging.DEBUG
    coloredlogs.install(level=level)

    if args["generate"]:
        task = TaskParser(definition_dir=definition_dir).parse()
        CodeGenerator(task=task, output_dir=output_dir).generate()
        return

    if args["run"]:
        algorithms = {}
        for f in args["--algorithm"]:
            slot, path = f.split(":", 2)
            algorithms[slot] = path

        ModuleRunner(args["<executable>"], algorithms).run()
        return

    if args["evaluate"]:
        case = args["--test-case"]
        phase = args["--test-phase"]

        slots = {}
        for f in args["<file>"]:
            slot, path = f.split(":", 2)
            slots[slot] = path

        ProblemEvaluator(input_dir, output_dir, "evaluation1").evaluate(slots=slots)
        return

    if args["cpp"] and args["module"] and args["flags"]:
        dir = pkg_resources.resource_filename("taskwizard.language.cpp", "module_lib")
        print("-std=c++14 -I %s %s" % (dir, os.path.join(dir, "taskwizard", "support_proto.cpp")))
        return

    raise NotImplementedError

if __name__ == "__main__":
    main()
