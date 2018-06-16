from .test_utils import assert_no_interface_errors

interface = '''
    function sum(a, b);
    
    procedure init(a, b[], c[][], d[][][]);
    
    function accept_callbacks(a) callbacks {
        function sum(a, b);
        procedure test(a);
        procedure void();
    }
    
    procedure with_callbacks(a) callbacks {
        procedure callback(a);
    }
    
    main {
        read a, b;
        call c = sum(a, b);
        write c;
        
        read c;
        for i to 10 {
            read d[i];
            for j to 20 {
                read e[i][j];
                for k to 30 {
                    read f[i][j][k];
                }
            }
        }
        
        call init(c, d, e, f);
        
        read g; 
        call h = accept_callbacks(g) callbacks {
            function sum(a, b) {
                return a + b;
            }
            procedure test(a) {
                write a;
            }
        }
        write h;
        
        read i; 
        call with_callbacks(i);
    }
'''


def test_parsing():
    assert_no_interface_errors(interface)
