from turingarena import *
from turingarena.evallib.algorithm import run_algorithm

ponged = False
try:
    with run_algorithm(submission.source) as p:
        def pong():
            global ponged
            ponged = True
            p.exit()


        p.procedures.ping(callbacks=[pong])
except AlgorithmError:
    pass
