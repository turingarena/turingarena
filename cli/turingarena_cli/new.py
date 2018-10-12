from __future__ import print_function

import logging
import os
import sys
from argparse import ArgumentParser

from turingarena_cli.command import Command
from turingarena_cli.base import BASE_PARSER

evaluator_template = """\
from turingarena import run_algorithm, submission, evaluation


# the solution submitted by the user, source is the default name
submitted_solution = submission.source

# run the solution
with run_algorithm(submitted_solution) as p:
    
    # call a procedure:
    p.procedures.p(a, b, c, callbacks=[cb1, cb2])
    
    # or call a function:
    result = p.functions.f(a, b)
    

# return the evaluation result (use whatever dict you like)
evaluation.data(dict(all_passed=True))
"""

interface_template = """\
// this is a default interface.txt file
// in the interface.txt you describe the structure of your problem
    
// you can insert here your constant declarations:
const ANSWER_TO_LIFE_THE_UNIVERSE_AND_EVERYTHING = 42;
    
// you insert here your procedures declarations:
procedure p(a, b[], c[][]) callbacks {
    function cb1(a, b);
    procedure cb2(a);
}

// or functions declarations:
function f(a, b); // no callbacks
    
// this is your main block, you need to put into it the code that 
// will be translated in the skeleton for the various languages
main {
    read a, b;
    call res = f(a, b);
    write res;
}    
"""


class NewCommand(Command):
    def run(self):
        name = self.args.name

        logging.info("Creating new problem {}".format(name))
        logging.info("Making directory {}/".format(name))

        try:
            os.makedirs(name)
        except FileExistsError:
            sys.exit("Directory {}/ already exists in this directory!".format(name))
        os.chdir(name)

        # TODO: if directory is not a git repository, initialize empty repository

        logging.info("Writing default interface.txt")
        with open("interface.txt", "w") as f:
            print(interface_template, file=f)

        logging.info("writing default evaluator.py")
        with open("evaluator.py", "w") as f:
            print(evaluator_template, file=f)

        logging.info("making directory solutions/")
        os.makedirs("solutions/")
        print("Problem {name} created in directory {name}".format(name=name))
        print("Start editing your default interface.txt and evaluator.py files!")

    PARSER = ArgumentParser(
        description="Create a new Turingarena problem",
        add_help=False,
        parents=[BASE_PARSER]
    )
    PARSER.add_argument("name", help="problem name")


NewCommand.PARSER.set_defaults(Command=NewCommand)
