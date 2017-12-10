from tempfile import TemporaryDirectory

from turingarena.protocol.client import ProxiedAlgorithm
from turingarena.sandbox.algorithm import Algorithm
from turingarena.sandbox.cpp import CppAlgorithmSource


def test_valid_types():
    protocol_name = "turingarena.protocol.tests.types_valid"
    name = "types_valid"

    source_text = """
        int i, *ia, **iaa;
    
        int get_i() {
            return i;
        }
        
        int get_ia(int j) {
            return ia[j];
        }
        
        int get_iaa(int j, int k) {
            return iaa[j][k];
        }
    """

    algorithm_source = CppAlgorithmSource(
        filename=None,
        language="c++",
        text=source_text,
        protocol_name=protocol_name,
        interface_name=name,
    )

    with TemporaryDirectory() as temp_dir:
        algorithm_executable = algorithm_source.compile(name=name, dest_dir=temp_dir)
        algorithm = Algorithm(source=algorithm_source, executable=algorithm_executable)

        impl = ProxiedAlgorithm(
            algorithm=algorithm,
        )

        iaa = [
            [1, 2, 3],
            [],
            [4, 5],
        ]
        ia = [len(x) for x in iaa]
        i = len(ia)

        with impl.run(i=i, ia=ia, iaa=iaa) as p:
            assert i == p.get_i()
            for j in range(i):
                assert ia[j] == p.get_ia(j)
                for k in range(ia[j]):
                    assert iaa[j][k] == p.get_iaa(j, k)
