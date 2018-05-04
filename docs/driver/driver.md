# Driver Protocol

The driver is a tool offered byt TuringArena,
used to start a sandboxed process and interact with it
by directly calling its functions.

## Protocol

The driver manager exposes a directory with the following named pipes:

Request pipes:
- `interface`
- `source`
- `language`

Response pipes:
- `connection_dir`

To start a process, the client does the following.

1. Writes the name of the interface to the `interface` pipe.
2. Writes the name of the source to the `source` pipe.
3. Writes the source language to the `language` pipe.
4. Reads from `connection_dir` until EOF.

## Interaction with process

The data read from `connection_dir` is an absolute path
of a directory, where the following pipes are exposed.

- `input`
- `output`

For each communication block, the evaluator does the following.
1. Opens the `input` pipe, writes one or more requests, then closes the pipe (flushing the data).
2. Opens the `output` pipes, reads it until EOF, then closes it.
3. Performs a `wait` on the sandbox.

The following data is passed through the `input` and `output` pipes:

- `input`:
    - zero or more requests which do *not* expect any response,
    - exactly one request which expects a response.
- `output`:
    - the response to the last request in `input`
    - zero or more of the following:
        - a request,
        - the corresponding response, if expected.

Reaching EOF in the `output` pipe
denotes the end of the communication block.

### Example

Imagine an algorithm which is asked to find a cycle in a given graph.
It implements three functions:

- `find_cycle(int N, int M, int E[])` which received in input a graph, 
finds a cycle and saves it in global variables (it does not return anything).
- `get_cycle_length()` which returns the length of the cycle found.
- `get_cycle_node(int i)` which returns the `i`-th node of the cycle.

Here is the possible content of the `input` and `output` streams.

`input`:
```

call
find_cycle
[... parameters of find_cycle ...]

call
get_cycle_length
[... parameters of get_cycle_length ...]
```

`output`:
```
3

call
get_cycle_node
[... parameter i=0 for get_cycle_node ...]
42

call
get_cycle_node
[... parameter i=1 for get_cycle_node ...]
12

call
get_cycle_node
[... parameter i=2 for get_cycle_node ...]
80

exit
```