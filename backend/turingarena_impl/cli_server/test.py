import pytest


def test_cmd(args):
    cli = ["-p", "no:cacheprovider", "-n", "8"]
    if args.pytest_arguments:
        cli += args.pytest_arguments
    return_code = pytest.main(cli)
    exit(return_code)
