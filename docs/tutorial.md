# A guided tour of an example problem

Before creating your first problem,
have a look at some of the examples problems
provided along with TuringArena itself.
They all share the same directory structure,
but they also highlight different features of the TuringArena system.

Let's start with the simplest problem first:
`sum_of_two_numbers`,
that you can find in the directory `examples/sum_of_two_numbers/`.
In this problem,
one is asked to write a function (called `sum`)
that computes the sum of two numbers given as arguments.

You can find examples of correct solutions in the `solutions/` directory,
written in several programming languages.
For example, in C++, a correct solution is:
```c++
int sum(int a, int b) {
    return a + b;
}
```

You can test this solution by running
```bash
turingarena evaluate solution/correct.cpp
```

Try it yourself:
write your own solution, in the same directory, and test it!

## Interfaces and multiple programming languages

Notice that the same problem can evaluate solutions written in
different programming languages.
This is possible since the problem
defines an **interface**
between the evaluator and the solution code.

First of all, the interface specifies one or more **functions** that the solution must implement.
When a solution is evaluated,
a **process** is started.
This process receives some *input*,
*calls* the functions implemented in the solution,
and, according to the results of the functions,
it produces some *output*.

Besides the functions to be implemented in the solution,
the interface also specifies the behavior of the the solution process
(called the **communication protocol**):

- how it receives its input,
- how it calls the functions,
- how it produces its output.

The interface is defined in the file `interface.txt`.

### Sum of two numbers

Have a look at the file `interfaces.txt`
for the `sum_of_two_numbers` problem.
There is only one function defined, `sum`, which accepts two parameters and returns a value.
In this case, the communication protocol is very simple:
1. the process *reads* two variables: `a` and `b`,
2. the process *calls* the `sum` function, passing `a` and `b` as arguments, and saves the returned value into a variable `c`,
3. the process *writes* the variable `c`.

## Evaluator

The actual evaluation of a solution is done by a program, called **evaluator**.
The evaluator is the main part of a problem:
it prepares the input sent to the solution,
and judges its output,
producing a *feedback* for the solution.

The evaluator can start a solution process
as many times as it wants,
using the TuringArena library,
and can communicate with a process,
by *calling directly the functions*
implemented by the solutions.
The TuringArena engine automatically
generates the input, sends it to the solution process, receives its output,
and makes it available to the evaluator.
Via the TuringArena engine, the evaluator enngages in a virtual direct communication with  the solution, as if the functions implemented by the solution
were written in the same programming language as the evaluator.

This is possible as long as the calls performed by the evaluator respect the communication protocol defined in `interface.txt`,
otherwise TuringArena shows an error message.

### Sum of two numbers

In this example problem, the evaluator is written in Python,
in the file `evaluate.py`.

It performs a fixed number of iterations.
At each iteration, it first generates a random pair of numbers `a` and `b` (a test case).
Then, it starts a new solution process,
and calls the `sum` function, passing the values of `a` and `b` just generated.
If `sum` behaves correctly and returns the value `a+b`, the evaluator considers this test case *passed*.
If there is an error in the solution process,
say, the solution attempts to open a file,
executes a disallowed system call,
or takes too long to answer,
then the evaluator is notified by TuringArena,
and considers the test case *failed*.
The test case is also considered *failed*
if `sum` returns a value which is not
the sum of `a` and `b`.

The evaluator reports the outcome of each test case.
At the end,
the evaluator marks the goal `correct`
as achieved if all the test cases are passed.

In general, a problem may have several goals,
which are achieved depending on, say,
how many functionalities are implemented,
the quality of the outputs,
and the computational efficiency of the solution.
