from turingarena.protocol.tests.util import cpp_implementation


def test_valid_types():
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

    iaa = [
        [1, 2, 3],
        [],
        [4, 5],
    ]
    ia = [len(x) for x in iaa]
    i = len(ia)

    with cpp_implementation(
            source_text=source_text,
            protocol_name="turingarena.protocol.tests.types_valid",
            interface_name="types_valid",
    ) as impl:
        with impl.run(i=i, ia=ia, iaa=iaa) as p:
            assert i == p.get_i()
            for j in range(i):
                assert ia[j] == p.get_ia(j)
                for k in range(ia[j]):
                    assert iaa[j][k] == p.get_iaa(j, k)
