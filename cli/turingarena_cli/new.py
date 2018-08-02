import os

from turingarena_cli.common import ok, info, die

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


def new_problem(name):
    ok("Creating new problem {}".format(name))
    info("Making directory {}/".format(name))

    try:
        os.makedirs(name)
    except FileExistsError:
        die("Directory {}/ already exists in this directory!".format(name))
    os.chdir(name)

    info("Writing default interface.txt")
    with open("interface.txt", "w") as f:
        print(interface_template, file=f)

    info("writing default evaluator.py")
    with open("evaluator.py", "w") as f:
        print(evaluator_template, file=f)

    info("making directory solutions/")
    os.makedirs("solutions/")
    ok("Problem {name} created in directory {name}/".format(name=name))
    ok("Start editing your default interface.txt and evaluator.py files!")
