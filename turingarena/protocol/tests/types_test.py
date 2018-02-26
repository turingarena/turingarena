from turingarena.test_utils import define_many


def test_valid_types():
    for algo in define_many(
            interface_text="""
                var int i;
                var int[] ia;
                var int[][] iaa;
            
                function get_i() -> int;
                function get_ia(int j) -> int;
                function get_iaa(int j, int k) -> int;
            
                main {
                    input i;
                    alloc ia, iaa : i;
                    for(j : i) {
                        input ia[j];
                        alloc iaa[j] : ia[j];
                        for(k : ia[j]) {
                            input iaa[j][k];
                        }
                    }
            
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
            sources={
                'python': """if True:
                    from __main__ import i, ia, iaa
    
                    def get_i():
                        return i
    
                    def get_ia(j):
                        return ia[j]
    
                    def get_iaa(j, k):
                        return iaa[j][k]
                """,
                'c++': """
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
            },
    ):
        iaa = [
            [1, 2, 3],
            [],
            [4, 5],
        ]
        ia = [len(x) for x in iaa]
        i = len(ia)

        with algo.run(global_variables=locals()) as (process, p):
            assert i == p.get_i()
            for j in range(i):
                assert ia[j] == p.get_ia(j)
                for k in range(ia[j]):
                    assert iaa[j][k] == p.get_iaa(j, k)
