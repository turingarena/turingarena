# Submission evaluation CLI

*Submission Evaluation CLI* is a set of conventions,
useful to specify *submissions* and receive *evaluations*
using a Command Line Interface.

## Submissions

A command line program can accept

- zero or more submissions identified by a *base name*, and
- optionally, a *default* submission.

(Usually, a command accepts only a *default* submission.)

Base names contain only `a-zA-Z0-9_`.

### Options

Four options are provided

- `--file` or `-F`,
- `--file-as-string`,
- `--string` or `-S`,
- `--string-as-file`.

For each of the four option, the argument has the form
`[<submission>/]<name>=<value>`, where:

- `<submission>` is the base name of the submission (omitted for the default submission), 
- `<value>` is either:
    - a path pointing to a regular file, for `--file` or `--file-as-string`,
    - a string, for `--string` or `--string-as-file`.

### Source file arguments

A sequence of paths, say, given as a positional argument,
can be used to define fields.

For a single path, it is equivalent to

- `--file source=<path>`, and
- `--string source_filename=<path>`.

For more than one path, it is equivalent to:

- `--file source1=<path>`,
- `--string source1_filename=<path>`.
- `--file source2=<path>`,
- `--string source2_filename=<path>`,
- and so on.
