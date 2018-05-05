# How interfaces work

When the evaluator start a solution process and calls its functions,
the TuringArena engine automatically
generates the input, sends it to the solution process, receives its output,
and makes it available to the evaluator.
Thanks to the TuringArena engine, the evaluator engages in a virtual direct communication with the solution, as if the functions implemented by the solution
were written in the same programming language as the evaluator.

However, this is possible only as long as the calls performed by the evaluator respect the communication protocol defined in `interface.txt`,
otherwise TuringArena shows an error message.

## Try it yourself!

See what happens when your evaluator does not respect the interface you have defined.
For example:

- Function definitions.
    - Call a function which is not defined in the interface.
    - Call a function with the wrong number of arguments.
- Communication protocol.
    - Run a solution process without calling any functions.
    - Call an extra function at the end, which is not expected.
    - Call a function with an unexpected parameter value.
    (For example, change the interface to call first `sum(a,b)` and then `sum(b,a)`.
    Then, in the evaluator, call `sum` two times, passing the second time a different pair of arguments.)