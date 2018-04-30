import sys

import pytest


def test_cli(argv):
    """
    Usage:
        test [<pytestargs>...]

    Options:
        <pytestargs>  Options to pass to pytest
    """

    return_code = pytest.main(
        [
            "-p", "no:cacheprovider",
            "-n", "8",
        ] + argv
    )
    sys.exit(
        return_code
    )
