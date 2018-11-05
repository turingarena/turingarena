import pytest

from turingarena.driver.exceptions import AlgorithmRuntimeError
from turingarena_impl.driver.tests.test_utils import define_algorithm

INTERFACE_TEXT = """
    procedure p();
    main {
        call p();
        checkpoint;
    }
"""


def test_timeout():
    with define_algorithm(
            interface_text=INTERFACE_TEXT,
            language_name="C++",
            source_text="""
                void p() { for(;;); }
            """,
    ) as algo:
        with pytest.raises(AlgorithmRuntimeError) as exc_info:
            with algo.run() as p:
                p.procedures.p()
                p.checkpoint()
        assert "stopped sending data" in exc_info.value.message
        assert "timeout expired" in exc_info.value.message


def test_io_blocked():
    with define_algorithm(
            interface_text=INTERFACE_TEXT,
            language_name="C++",
            source_text="""
                #include <cstdio>
                void p() { for(;;) scanf(" "); }
            """,
    ) as algo:
        with pytest.raises(AlgorithmRuntimeError) as exc_info:
            with algo.run() as p:
                p.procedures.p()
                p.checkpoint()
        print(exc_info.value.message)
        assert "stopped sending data" in exc_info.value.message
        assert "timeout expired" in exc_info.value.message


def test_io_garbage():
    with define_algorithm(
            interface_text=INTERFACE_TEXT,
            language_name="C++",
            source_text=r"""
                #include <cstdio>
                void p() { for(;;) printf("garbage\n"); }
            """,
    ) as algo:
        with pytest.raises(AlgorithmRuntimeError) as exc_info:
            with algo.run() as p:
                p.procedures.p()
                p.checkpoint()
        assert "sent invalid data" in exc_info.value.message
