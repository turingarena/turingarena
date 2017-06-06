import sys
from interfaces.exampleinterface import exampleinterface

iface = exampleinterface(sys.stdin, sys.stdout)

iface.N = 10
iface.M = 100
iface.A.alloc(1, 100)

for i in range(1, 1+100):
    iface.A[i] = i*i

S = iface.solve(3)
print("Answer:", S, file=sys.stderr)
