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
- `status`

TODO.
