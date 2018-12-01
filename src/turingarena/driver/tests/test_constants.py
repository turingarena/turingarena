from turingarena.driver.tests.test_utils import define_algorithms


def test_constant():
    for algo in define_algorithms(
            interface_text="""
                const c = 2;
                procedure p();
                main {
                    for i to c {
                        call p();
                        checkpoint;
                    }
                }
            """,
            sources={
                'C++': "void p() {}",
                'Python': "def p(): pass",
            }
    ):
        with algo.run() as p:
            for i in range(2):
                p.procedures.p()
                p.checkpoint()
