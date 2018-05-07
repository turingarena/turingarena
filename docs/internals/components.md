# TuringArena components

TODO: evaluations, web servers, CLI, etc.

## Sandbox Manager

A library that allows to run the code of a submission in a *sandbox*,
and connect to it via *`stdin`/`stdout`*.
Multiple isolated processes can be started,
running concurrently,
even executing the same solution code.

## Interface Manager

A tool that allows to *communicate* with a solution process by directly calling its *functions*
(possibly accepting *callbacks*).

The communication is realized using `stdin`/`stdout`,
with a *highly-customizable protocol*,
in such a way that it is easy
(though not required)
to implement a solution
using directly `stdin` and `stdout`.
