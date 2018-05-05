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

A **submission** is a collection of **fields**, each comprising

- a **name**, containing only ASCII lowercase letters (`a-z`) and underscores (`_`), and
- a **value**, which can be either a **string** or a **file**.

Field names must be unique inside a submission, and are associated to a single value.

- String values are (short) *Unicode strings*.
- File values are files (i.e., byte buffers) in an *unspecified format*.
(File values can be associated with metadata such as filename and MIME type,
but these metadata should not be used as part of the evaluation.)

### Rationale

The format of submissions is chosen so that it maps naturally to HTML *forms*,
and the `multipart/form-data` content type in HTTP requests, for Web based APIs.

## Evaluation and evaluators

An evaluation is a stream of **events**.
Events can be of two types, **text** and **data**,
and contain a **payload**.

The payload of *text* events is a Unicode string.
The payload string must be non-empty, and either:
- does *not* contain any line terminator, or
- consist of a single line terminator only.

The payload of *data* events is a JSON object.

An evaluation is possibly associated with other metadata such as

- a checksum of the evaluated submission
- a checksum of the evaluator and its data
- the time of evaluation
- extra metadata provided at the time of submission

An **evaluator** is a program that takes a submission in input
and produces an evaluation as output.
