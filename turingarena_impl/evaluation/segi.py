import os
import secrets
import selectors
import subprocess
import time
from contextlib import ExitStack, contextmanager

from turingarena_impl.evaluation.submission import SubmissionFieldType


def submission_environ(submission_fields):
    prefixes = {
        SubmissionFieldType.STRING: "SUBMISSION_VALUE_",
        SubmissionFieldType.FILE: "SUBMISSION_FILE_",
    }
    return {
        prefixes[v.type + name.upper()]: v
        for name, v in submission_fields.items()
    }


@contextmanager
def process_stdout_pipe(cmd, *, env=None):
    with ExitStack() as stack:
        read_pipe_fd, write_pipe_fd = os.pipe2(os.O_NONBLOCK)

        def close_pipes():
            os.close(read_pipe_fd)
            if write_pipe_fd is not None:
                os.close(write_pipe_fd)

        stack.callback(close_pipes)

        stack.enter_context(subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=write_pipe_fd,
            env=env,
        ))
        os.close(write_pipe_fd)
        write_pipe_fd = None
        yield read_pipe_fd


def segi_subprocess(submission, cmd, *, env=None):
    if env is None:
        env = {}

    data_begin, data_end = (
        f"--begin-data-{secrets.token_hex(5)}--",
        f"----end-data-{secrets.token_hex(5)}--",
    )

    env = {
        **env,
        "EVALUATION_DATA_BEGIN": data_begin,
        "EVALUATION_DATA_END": data_end,
        **submission_environ(submission),
    }

    with process_stdout_pipe(cmd, env=env) as fd:
        yield from get_lines(fd)


def get_lines(fd, interval=0.02):
    """
    Reads from the given file descriptor and generates text parts.
    Each text part is either:
    - non-empty and without line terminators '\n', or
    - a single line terminator '\n'

    Input on a single line is split into separate events
    about once each `interval` seconds.
    """

    # TODO: implement splitting also by length

    selector = selectors.DefaultSelector()
    selector.register(fd, selectors.EVENT_READ)
    buffer = ()
    timeout = 0
    while True:
        before = time.monotonic()
        events = selector.select(timeout)
        after = time.monotonic()
        timeout -= (after - before)
        if not events:
            yield from buffer
            selector.select()
            timeout = interval

        data = os.read(fd, 2 ** 16)
        if not data:
            break

        lines = data.splitlines(keepends=True)
        if lines[-1].endswith(b"\n"):
            lines.append(None)

        lines[0] = b"".join(buffer) + lines[0]
        for line in lines[:-1]:
            assert line.endswith(b"\n")
            yield from generate_text_part(line[:-1])
            yield b"\n"
            timeout = interval

        buffer = generate_text_part(lines[-1])
    yield from buffer


def generate_text_part(part):
    if part:
        yield part


def test_get_lines():
    with process_stdout_pipe(["bash", "-c", """
        for i in `seq 9`; do
            for i in `seq 9`; do
                echo -n $i
                sleep 0.005
            done
            echo ' line end'
        done
        echo
    """]) as fd:
        for line in get_lines(fd):
            print(line)
