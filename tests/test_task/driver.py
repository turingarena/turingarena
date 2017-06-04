import sys
from interfaces.exampleinterface import exampleinterface

iface = exampleinterface(sys.stdin, sys.stdout)

iface.data.N = 10
iface.data.M = 100
iface.data.A.alloc(1, 100)

for i in range(1, 1+100):
    iface.data.A[i] = i*i

iface.solve(3)
