import pytest

from turingarena.algorithm import load_algorithm

sources = {
    "c++": """
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
    """,
    "python": """if True:
        from skeleton import i, ia, iaa
    
        def get_i():
            return i
    
        def get_ia(j):
            return ia[j]
    
        def get_iaa(j, k):
            return iaa[j][k]
    """
}


@pytest.mark.parametrize("language,source_text", sources.items(), ids=list(sources.keys()))
def test_valid_types(language, source_text):
    with load_algorithm(
            interface_text="""
                var int i;
                var int[] ia;
                var int[][] iaa;
            
                function get_i() -> int;
                function get_ia(int j) -> int;
                function get_iaa(int j, int k) -> int;
            
                init {
                    input i;
                    alloc ia, iaa : i;
                    for(j : i) {
                        input ia[j];
                        alloc iaa[j] : ia[j];
                        for(k : ia[j]) {
                            input iaa[j][k];
                        }
                    }
                }
            
                main {
                    var int o;
                    var int[] oa;
                    var int[][] oaa;
            
                    call get_i() -> o;
                    alloc oa, oaa : i;
                    for(j : i) {
                        call get_ia(j) -> oa[j];
                        alloc oaa[j] : ia[j];
                        for(k : ia[j]) {
                            call get_iaa(j, k) -> oaa[j][k];
                        }
                    }
            
                    output o;
                    for(j : i) {
                        output oa[j];
                        for(k : ia[j]) {
                            output oaa[j][k];
                        }
                    }
                }
            """,
            language=language,
            source_text=source_text,
    ) as algo:
        iaa = [
            [1, 2, 3],
            [],
            [4, 5],
        ]
        ia = [len(x) for x in iaa]
        i = len(ia)

        with algo.run(global_variables=dict(iaa=iaa, ia=ia, i=i)) as p:
            assert i == p.call.get_i()
            for j in range(i):
                assert ia[j] == p.call.get_ia(j)
                for k in range(ia[j]):
                    assert iaa[j][k] == p.call.get_iaa(j, k)
