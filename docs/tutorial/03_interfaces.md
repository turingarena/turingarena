# Interfaces

With TuringArena, the same problem can evaluate solutions written in
different programming languages.
This is possible since the problem
defines an **interface**
between the evaluator and the solution code.

First of all, the interface specifies one or more **functions** that the solution must implement,
but this is not all.
When a solution process is started,
the communication with the evaluator
happens as follows. The process:

- receives some *input*,
- *calls* the functions implemented in the solution,
and
- produces some *output*, according to the results of the functions called.

The interface specifies how the solution process behaves:
how it receives its input, how it calls the functions, how it produces its output.
The behavior of the solution process is called **communication protocol**.

The interface (both the functions and the communication protocol) is defined in the file `interface.txt`.

## Interface of `sum_of_two_numbers`

Have a look at the file `interfaces.txt`
for the `sum_of_two_numbers` problem.
There is only one function defined, `sum`, which accepts two parameters and returns a value.
In this case, the communication protocol is very simple:

1. the process *reads* two variables: `a` and `b`,
2. the process *calls* the `sum` function, passing `a` and `b` as arguments, and saves the returned value into a variable `c`,
3. the process *writes* the variable `c`.

## Try it yourself!

Change the interface of `sum_of_two_numbers`.
Here are some suggestions.

- Change `sum` to accept three arguments.
- For every pair `a` and `b` (read only once in input),
call both `sum(a,b)` and `sum(b,a)`.

Remember that you have to change both the interface
*and* the evaluator!
