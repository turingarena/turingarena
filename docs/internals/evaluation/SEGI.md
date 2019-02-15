# Submission Evaluation Gateway Interface (SEGI)

The **Submission Evaluation Gateway Interface (SEGI)**
is a set of conventions used to communicate with an evaluator in order to evaluate a submission.
It is inspired by the Common Gateway Interface (CGI), used for responding to HTTP requests.

SEGI is a low-level interface:
it is designed to easily integrate evaluators written using different programming languages and technologies,
as it relies only on the abstraction offered by POSIX.

## General assumptions

In SEGI, the evaluations occur sequentially in a (POSIX) process,
and the communication with the evaluator program
occurs only through the process context.
More specifically, the following assumptions hold.

- For each submission to evaluate, the evaluator program is executed once.
How the evaluator program is loaded and started is not specified by SEGI.
Possible options:
    - Launching an executable as a child process.
    - Running a Python script in an existing Python interpreter process.
    - ...
- At most one submission is evaluated in the same process at the same time.
(But more than one submission may be evaluated in the same process sequentially.)
- The evaluation stops when the evaluator program terminates.
How the termination of the evaluator program is determined is not specified by SEGI.
- No extra arguments depending on the submission are passed directly to the evaluator program
(say, function arguments).
- No output is taken directly from the evaluator program
(say, function return value).
- All the communication occurs through:
    - enviroment variables,
    - standard file descriptors, and
    - files on the local filesystem, whose path is specified in enviroment variables.
- Other data can be provided to the evaluator program, preferably through enviroment variables,
as long as they do not depend on the submission.

### Rationale

Thanks to the above assumptions, the evaluator program can easily invoke other executables (as child processes)
as part of the evaluation.
Indeed, all the relevant process context (enviroment variables and standard file descriptors)
is inherited by child processes by default.

SEGI, as CGI, has the drawback of introducing overhead
due to the usage of system calls for process management.
However, while this overhead may be significant for HTTP requests,
it is totally negligible for submission evaluations,
which are supposed to be infrequent and take up to a few seconds.
Also, the security implications of CGI,
such as the ability to set some enviroment variables to arbitrary values,
are a lesser concern for SEGI since the evaluator code
is already considered unsafe, and it is run in a container.

## Submission

For each field in the submission, an environment variable is provided, defined by:

- name: `SUBMISSION_FILE_` followed by the field name *to upper case*,
- value: the *absolute* path to a *regular* file on the filesystem,
whose content and basename correspond to the submission file.
(The process must be able to open the file for reading.)

## Evaluations

An evaluation is generated from the process `stdout`.

Normally, whatever is written to `stdout`
results in *text* events (with the requirement that line terminators
are recorded in their own event).

In order to generate *data* events,
escape sequences are used.
Specifically,
four hard-to-guess strings are provided as enviroment variables:

- `EVALUATION_DATA_BEGIN`
- `EVALUATION_DATA_END`
- `EVALUATION_FILE_BEGIN`
- `EVALUATION_FILE_END`

These strings must not be valid JSON.

### Data events 

In order to generate data events,
the process must:

1. print a line terminator
2. print the value of `EVALUATION_DATA_BEGIN`, followed by a line terminator
3. for every data event to generate, print its payload as JSON in a single line, followed by a line terminator
4. print  the value of `EVALUATION_DATA_END`, followed by a line terminator

### File events 

In order to generate file events,
the process must:

1. print a line terminator
2. print the value of `EVALUATION_FILE_BEGIN`, followed by a line terminator
3. print a number of headers, as described below, each one followed by a line terminator (like HTTP)
4. print an empty line
5. print the body of the event, as described below
6. print a line terminator, wich is not part of the body
7. print the value of `EVALUATION_FILE_END`, followed by a line terminator

At the moment only 2 headers are supported:
- `Content-type`: indicate the MIME type of the file (exactly as HTTP, defaults to text/plain)
- `X-SEGI-as`: indicate how to interpret the body of the message, it can contain the following values:
    * `content`: interpretate the body as content of the file. (default)
    * `path`: interpretate the body as a path to the file. 
    
If the `X-SEGI-as: path` header is specified, we must assume that after the event is generated, the file is 
not opened by the evaluator and it will never be opened again until the end of the evaluation. Every subsequent 
interaction with the file is undefined behaviour. In particular, you must not trigger 2 events with the same path. 

Rationale: the ownership of the file is transefed to the SEGI implementation, that can move, delete, modify it 
as it will. 

### Example

- `EVALUATION_DATA_BEGIN` is set to `--evaluation-data-begin-7e112fc35845cd01d454`
- `EVALUATION_DATA_END` is set to `--evaluation-data-end---46c11713eef6050e3ca6`

Consider the following `stdout` stream:
```
Hello.
I'm a very very ... very long line.

--evaluation-data-begin-7e112fc35845cd01d454
{"type": "goal", "name": "correct", "outcome": true}
{"type": "goal", "name": "linear_time", "outcome": false}
--evaluation-data-end---46c11713eef6050e3ca6
Nice! You got 60 points!

--evaluation-data-begin-7e112fc35845cd01d454
{"type": "score", "value": 60}
--evaluation-data-end---46c11713eef6050e3ca6
```

It could result in the following events:

- text: `"Hello."`
- text: `"\n"`
- text: `"I'm a very very ..."`
- text: `" very long line"`
- text: `"\n"`
- data: `{"type": "goal", "name": "correct", "outcome": true}`
- data: `{"type": "goal", "name": "linear_time", "outcome": false}`
- text: `"Nice! You got 60 points!"`
- text: `"\n"`
- data: `{"type": "score", "value": 60}`

### Rationale

TODO
