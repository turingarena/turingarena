# TuringArena

*Create algorithmic challenges!*

TuringArena is a toolkit to define challenges which require an algorithmic solution,
and to automatically test the code of solutions.

## Goals

* Writing a solution should require no usage of low-level primitives,
  not even reading/writing from a file or `stdin`/`stdout`.

* Defining a problem should require a knowledge as similar as possible to that
  required for writing solutions.

* A challenge may involve two or more solutions at the same time,
  written by different people,
  that can be evaluated together or against each other.

* Many programming languages should be supported,
  both for defining problems and for writing solutions,
  allowing different languages to inter-operate during the evaluation.
  (Say, a problem written in python can be used to test a solution written in C,
  two solutions written in C and Java can be evaluated against each other, etc.)

## Architecture

Differently from other solutions,
TuringArena is designed as a "library" instead of a "framework".
This means that a challenge defined with TuringArena
has the complete control on the process of evaluation,
and can make use of any subset of the tools provided by TuringArena.
