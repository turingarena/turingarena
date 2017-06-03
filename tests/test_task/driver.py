import sys
from interfaces.exampleinterface import exampleinterface

i = exampleinterface(sys.stdin, sys.stdout)

i.N = 10
i.M = 100
i.A.alloc(1,100)

i.A[3] = 5

i.call_solve()

i.downward_protocol()
