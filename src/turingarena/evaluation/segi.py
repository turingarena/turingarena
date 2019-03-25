import json
import os
import cgi
import secrets
import selectors
import subprocess
import base64
import time
from contextlib import ExitStack, contextmanager

from turingarena.evaluation.events import EvaluationEvent


def submission_environ(submission_fields):
    return {
        "SUBMISSION_FILE_" + name.upper(): path
        for name, path in submission_fields.items()
    }


@contextmanager
def process_stdout_pipe(cmd, **popen_kwargs):
    with ExitStack() as stack:
        read_pipe_fd, write_pipe_fd = os.pipe2(os.O_NONBLOCK)

        def close_pipes():
            os.close(read_pipe_fd)
            if write_pipe_fd is not None:
                os.close(write_pipe_fd)

        stack.callback(close_pipes)

        stack.enter_context(subprocess.Popen(
            cmd,
            **popen_kwargs,
            stdin=subprocess.DEVNULL,
            stdout=write_pipe_fd,
        ))
        os.close(write_pipe_fd)
        write_pipe_fd = None
        yield read_pipe_fd


def segi_subprocess(submission, cmd, env=None, **popen_kwargs):
    if env is None:
        env = {}

    data_begin, data_end, file_begin, file_end = (
        f"@DATA_BEGIN_{secrets.token_hex(5)}--".encode(),
        f"@DATA_END___{secrets.token_hex(5)}--".encode(),
        f"@FILE_BEGIN_{secrets.token_hex(5)}--".encode(),
        f"@FILE_END___{secrets.token_hex(5)}--".encode(),

    )

    env = {
        **os.environ,
        **env,
        "EVALUATION_DATA_BEGIN": data_begin,
        "EVALUATION_DATA_END": data_end,
        "EVALUATION_FILE_BEGIN": file_begin,
        "EVALUATION_FILE_END": file_end,
        **submission_environ(submission),
    }

    with process_stdout_pipe(cmd, **popen_kwargs, env=env) as fd:
        yield from process_segi_output(fd, data_begin, data_end, file_begin, file_end)


def process_segi_output(fd, data_begin, data_end, file_begin, file_end):
    parts = generate_chunks(fd)
    parts = split_line_terminators(parts)
    parts = join_text_parts(parts)
    yield from generate_events(parts, data_begin, data_end, file_begin, file_end)


def generate_events(parts, data_begin, data_end, file_begin, file_end):
    newline_event = EvaluationEvent(dict(type="text", payload="\n"))
    pending_newline = False
    for part in parts:
        if pending_newline and part == data_begin:
            assert next(parts) == b"\n"
            yield from parse_data_events(parts, data_end)
            pending_newline = False
        elif pending_newline and part == file_begin:
            assert next(parts) == b"\n"
            yield from parse_file_events(parts, file_end)
            pending_newline = False
        else:
            if pending_newline:
                yield newline_event
            pending_newline = False
            if part == b"\n":
                pending_newline = True
            else:
                yield EvaluationEvent(dict(type="text", payload=part.decode()))
    if pending_newline:
        yield newline_event


def collect_joinable_parts(parts):
    for part in parts:
        yield part
        if not part or part == b"\n":
            break


def join_text_parts(parts):
    while True:
        joinable_parts = list(collect_joinable_parts(parts))
        if not joinable_parts:
            break
        line = b"".join(joinable_parts[:-1])
        if line:
            yield line
        if joinable_parts[-1]:
            yield joinable_parts[-1]


def parse_data_events(parts, data_end):
    """
    ProcessManager a stream of parts,
    *after* '\n' $EVALUATION_DATA_BEGIN '\n',
    and until $EVALUATION_DATA_END '\n' is encountered.
    Generates the data event payloads parsed.
    """
    while True:
        line = b"".join(iter(lambda: next(parts), b"\n"))
        if line == data_end:
            break
        json_data = json.loads(line)
        assert isinstance(json_data, dict)
        assert "type" in json_data
        assert isinstance(json_data["type"], str)
        yield EvaluationEvent(json_data)


def parse_header(line):
    main, params = cgi.parse_header(line.decode())
    name, value = main.split(": ", 1)
    return name.lower(), value, params


def process_headers(headers, body):
    payload = {}
    if "content-type" in headers:
        value, params = headers["content-type"]
        payload["content_type"] = value
        assert params == {}
    else:
        payload["content_type"] = "text/plain"

    if "x-segi-as" in headers:
        segi_as, params = headers["x-segi-as"]
        assert params == {}
        assert segi_as in ("path", "content")
    else:
        segi_as = "content"

    if "content-disposition" in headers:
        value, params = headers["content-disposition"]
        assert value == "attachment"
        assert "filename" in params and len(params) == 1
        payload["filename"] = params["filename"]
    else:
        payload["filename"] = "file.txt"

    if segi_as == "path":
        with open(body, "rb") as f:
            content = f.read()
    else:
        content = body

    payload["content_base64"] = base64.encodebytes(content).decode().replace("\n", "")
    return payload


def parse_file_events(parts, file_end):
    line = b"".join(iter(lambda: next(parts), b"\n"))
    headers = {}
    while line != b"":
        name, value, params = parse_header(line)
        headers[name] = value, params
        line = b"".join(iter(lambda: next(parts), b"\n"))
    line = b"".join(iter(lambda: next(parts), b"\n"))
    body = []
    while line != file_end:
        body.append(line)
        line = b"".join(iter(lambda: next(parts), b"\n"))
    body = b"\n".join(body)

    yield EvaluationEvent(dict(type="file", payload=process_headers(headers, body)))


def split_line_terminators(parts):
    """
    Splits the parts so that '\n' occur in their own parts.
    """
    for part in parts:
        lines = part.splitlines(keepends=True)
        if not lines:
            yield b""
            continue
        if lines[-1].endswith(b"\n"):
            lines.append(None)

        for line in lines[:-1]:
            assert line.endswith(b"\n")
            yield line[:-1]
            yield b"\n"
        if lines[-1] is not None:
            yield lines[-1]


def generate_chunks(fd, line_timeout=0.02):
    """
    Reads from the given file descriptor and generates data chunks.
    If some data is read and '\n' is not encountered within `line_timeout` seconds,
    then an empty chunk is generated as a sentinel.
    """
    # FIXME: currently it generate sentinels also when no data is pending after '\n'
    selector = selectors.DefaultSelector()
    selector.register(fd, selectors.EVENT_READ)
    timeout = 0
    while True:
        before = time.monotonic()
        events = selector.select(timeout)
        after = time.monotonic()
        timeout -= (after - before)
        if not events:
            yield b""
            selector.select()
            timeout = line_timeout
        data = os.read(fd, 2 ** 16)
        if not data:
            break
        if b"\n" in data:
            timeout = line_timeout
        yield data


def test_get_lines():
    with process_stdout_pipe(["bash", "-c", """
        for i in `seq 9`; do
            for j in `seq 9`; do
                echo -n $j
                sleep 0.005
            done
            echo ' line end'
            echo
            echo B
            echo -n '{"a":'
            sleep 0.1
            echo $i '}'
            echo E
        done
        echo last text
    """], {}) as fd:
        for event in process_segi_output(fd, b"B", b"E"):
            print(event)
