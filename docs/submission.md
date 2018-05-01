# Submission evaluation

A **submission** is a *collection of one or more files and/or values*
that should be evaluated.
An **evaluator** is a *program* which evaluates a submission
and produces some *text* and/or *structured data*.

For algorithmic problems, a submission is usually a single file
containing the source code of the solution,
and possibly a value specifying the programming language used.
However, it is possible for a submission to contain more than one file,
for example if the different files are written by different people
and should be evaluated one against the other
(e.g., bots in a two-player game).

TuringArena defines a standard way in which a submission
is evaluated by an evaluator.

## Submissions

The format of submission is chosen so that it maps naturally to HTML *forms*,
and the `multipart/form-data` content type in HTTP requests for Web based APIs.

A **submission** is a collection of **fields**, each comprising

- a **name**, containing only ASCII lowercase letters (`a-z`) and underscores (`_`), and
- a **value**, which can be either a **string** or a **file**.

Names must be unique inside a submission, and are associated to a single value (unlike HTML forms).

- String values are (short) *Unicode strings*.
- File values are files (i.e., byte buffers) in an *unspecified format*.
(File values can be associated with metadata such as filename and MIME type,
but these should not be used as part of the evaluation.)

## Evaluation and evaluators

An evaluation comprises:

- a **text**, which is a stream of text,
- a **data**, which is a JSON object.

An evaluation is possibly associated with other metadata such as
- a checksum of the evaluated submission
- a checksum of the evaluator and its data
- the time of evaluation
- extra metadata provided 

An **evaluator** is a program that takes a submission in input
and produces an evaluation as output.
