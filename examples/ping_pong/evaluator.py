from turingarena import *
from turingarena.driver.exceptions import AlgorithmError

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

evaluation.data(dict(goals=dict(ponged=ponged)))
