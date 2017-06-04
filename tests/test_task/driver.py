import sys
from interfaces.exampleinterface import exampleinterface

i = exampleinterface(sys.stdin, sys.stdout)

i.data.N = 10
i.data.M = 100
i.data.A.alloc(1,100)

i.data.A[3] = 5

i.call_solve()

i.downward_protocol()
