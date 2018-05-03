# Sandbox Process Management Protocol

A protocol for interacting with a running sandbox is described.

- The sandbox is considered already running. How the sandbox is started is not specified here.
- Only one call that can be performed: `wait`, which:
    - specifies whether to request the termination of the process,
    - returns the current status of the process.

## Protocol

The sandbox process is associated with two named pipes:

- the `wait` pipe, and
- the `status` pipe.

The execution of a `wait` occurs as follows.

1. The client writes to the `wait` pipe (with open/write/close):
    - `0`, if the termination is desired, or
    - `1`, if the process should continue to run.
2. The client opens the `status` pipe, reads from it until EOF, then closes it.

The data read from the status pipe contains the following data, each on a different line:

1. The total CPU usage, in microseconds, of the process up to now (integer).
2. The amount of RAM currently allocated by the process, in bytes (integer, approximated).
3. A line of text describing the current status of the process, and possibly error conditions that occurred.

The sandbox process manager must accept any number of `wait` calls
which specify that the process should continue to run,
regardless of the actual status of the process
(running or terminated),
and exactly one call to `wait` with termination,
which must be the last call performed.

### Rationale

The sandbox process management protocol deliberately ignores error situations occurring *during* the execution of the process,
such as invalid syscalls, premature termination, and even compilation failures.
Indeed, a sandboxed process can and should be evaluated only on its visible behavior, i.e., what it reads/writes on the I/O pipes, and its consumption of computational resources (time and memory).

Any exceptional condition can be detected by only looking at the process I/O, e.g., a premature EOF in `stdout`.
In that case, the sandbox can be queried for the process status, which can be provided as a dignostic along with the description of the I/O error.

Example:
```
The program stopped producing output (process interrupted by signal 11)
```

Notice also that a program can misbehave in its I/O (say, by closing `stdout`) without the sandbox noticing any exceptional behavior.

Example:
```
The program stopped producing output (process running normally)
```

## Process termination

When a `wait` is performed requesting the termination of the process,
this means the evaluator is not interested in any more output provided by the process.
Hence, the process can be killed forcibly.
Nonetheless, the process is first given a little time (~50ms?) to terminate normally, so that the distinction
*terminated normally / forced termination* can be reported.

## Time and memory usage

The measurement of time and memory usage is intrinsecally different.

Time usage accumulates over time. Hence, the evaluator is only interested in the time usage of a *section* of the execution, which is computed as the difference between the values reported by the sandbox, before and after the section is executed.

On the other hand, the memory usage is a value measures in a snapshot in time.
We deliberately omit statistics of memory usage *during* the execution of a section, but only provide *point in time* information.
(It is believed that the evaluator is always able to evaluate the memory efficiency of an algorithm using only this kind of information.)
This can have unexpected consequences:
if the memory is only measured at the end of the execution,
then the answer will always be zero.
In order to limit the memory usage explicitly (besides the overall memory limit), one needs to introduce a checkpoint in the middle of the execution,
and verify that at that time the memory is below the desired limit.
