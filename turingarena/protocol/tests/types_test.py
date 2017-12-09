from tempfile import TemporaryDirectory

import pkg_resources

from turingarena.protocol.proxy.python.engine import Implementation
from turingarena.sandbox.compile import sandbox_compile


def test_valid_types():
    with TemporaryDirectory() as temp_dir:
        protocol_name = "turingarena.protocol.tests.types_valid"
        name = "types_valid"

        sandbox_compile(
            dest_dir=temp_dir,
            source_filename=pkg_resources.resource_filename(
                __name__, f"types_valid.cpp"
            ),
            protocol_name=protocol_name,
            interface_name=name,
            algorithm_name=name,
            check=True,
        )

        impl = Implementation(
            work_dir=temp_dir,
            protocol_name=protocol_name,
            interface_name=name,
            algorithm_name=name,
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
