# Submission evaluation CLI

*Submission Evaluation CLI* is a set of conventions,
useful to specify *submissions* and receive *evaluations*
using a Command Line Interface.

## Submissions

A submission field can be specified on a command line as a string
(either a positional argument or the argument of an option)
with the following syntax:

```
[ submission_name '/' ] field_name ( ':' path | '=' value )
```

- `submission_name` is used to identify a submission
(say, if multiple submissions are provided).
- `field_name` is the name of the field.
- `path` is the path of the submission file
- `value` is the content of the submission file
(if provided, a temporary file is created with the given content).

### Examples

```
source:file.py source_language=c++
a/source:file.py b/source:file2.py
```

### Rationale

The separator `:` is used for paths, since `bash` seems to auto-complete paths
after `:` is encountered.

## Positional arguments

A list of submission files can be also specified directly as positional arguments,
as long as their paths do not contain `:` nor `='.
Submission files given as positional arguments are mapped to field names
taken from a list of default field names.

The list of default field names can depend on the program.
By default, it contains only one name: `source`.

## Evaluations

A command line tool can output an evaluation
by printing its event stream to `stdout`,
in JSON Lines (http://jsonlines.org/) format.
