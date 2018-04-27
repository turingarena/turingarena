from turingarena import *

algorithm = submitted_algorithm()

ponged = False
try:
    with algorithm.run() as p:
        def pong():
            global ponged
            ponged = True
            p.exit()


        c = p.call.ping(pong=pong)
except AlgorithmError:
    pass

evaluation_result(goals=dict(ponged=ponged))
