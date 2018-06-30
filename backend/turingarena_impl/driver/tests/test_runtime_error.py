import pytest

from turingarena import AlgorithmRuntimeError
from turingarena_impl.driver.tests.test_utils import define_algorithm


def test_time_limit_error():
    with define_algorithm(
            interface_text="""
                procedure p();
                main {
                    call p();
                    checkpoint;
                }
            """,
            language_name="c++",
            source_text="""
                void p() { for(;;); }
            """,
    ) as algo:
        with pytest.raises(AlgorithmRuntimeError) as exc_info:
            with algo.run() as p:
                p.procedures.p()
                p.checkpoint()
        message, info = exc_info.value.args
        assert "SIGXCPU" in message
