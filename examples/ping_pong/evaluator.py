from turingarena import *

algorithm = submitted_algorithm()

ponged = False
try:
    with algorithm.run() as p:
        def pong():
            global ponged
            ponged = True
            p.exit()


        p.procedures.ping(callbacks=[pong])
except AlgorithmError:
    pass

evaluation_data(dict(goals=dict(ponged=ponged)))
