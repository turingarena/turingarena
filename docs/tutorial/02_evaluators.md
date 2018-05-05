# Evaluator

The evaluation of a solution is done by a program, called **evaluator**.
The evaluator is the most important part of a problem:
it prepares the input sent to the solution
and judges its output,
producing a *feedback*.

To test a solution,
the evaluator has to start a solution *process*,
using the TuringArena library.
Then, it can communicate with the process
by *calling directly the functions*
implemented by the solutions.
The evaluator can start a solution process
as many times as it wants.

We'll see later how the communication is realized.

## Evaluator of `sum_of_two_numbers`

In this example problem, the evaluator is written in Python,
in the file `evaluate.py`.

It tests the solution on several pairs of numbers `a` and `b` (called *test cases*), checking if the result of `sum(a,b)` is actually `a`+`b`.
It performs a fixed number of iterations, one per test case. In each iteration it does the following.

- It generates a random pair of numbers `a` and `b`.
- It starts a new solution process, and communicates with it.
    - It calls the `sum` function, passing the values of `a` and `b` just generated, and stores the result in a variable `c`.
- If `sum` behaves correctly and returns the value `c == a+b`, the evaluator considers this test case *passed*.
- If there is an error in the solution process,
say, the solution attempts to open a file,
executes a disallowed system call,
or takes too long to answer,
then the evaluator is notified by TuringArena,
and considers the test case *failed*.
- If `sum` returns a value which is not
the sum of `a` and `b`, the test case is also considered *failed*.

The evaluator reports the outcome of each test case.
At the end,
the evaluator marks the goal `correct`
as achieved if all the test cases are passed.

In general, a problem may have several goals,
which are achieved depending on, say,
how many functionalities are implemented,
the quality of the outputs,
and the computational efficiency of the solution.

## Try it yourself!

Try to modify the file `evaluator.py`. Some suggestions:

- Change the number of test cases.
- Make the numbers `a` and `b` smaller/larger.
- Make the evaluator stop as soon as a test case is failed.
- Test the solution on negative values.
