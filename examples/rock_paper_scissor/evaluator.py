from enum import Enum

from turingarena import *

n_moves = 10


class RPS(Enum):
    ROCK = 0
    PAPER = 1
    SCISSOR = 2


with run_algorithm(submission.player1) as p1, run_algorithm(submission.player2) as p2:
    players = (p1, p2)

    for p in players:
        p.procedures.start(n_moves)

    for i in range(n_moves):
        moves = [None, None]

        for j, p in enumerate(players):
            moves[j] = p.functions.play(i)

        for j, p in enumerate(players):
            outcome = (moves[j] - moves[1 - j]) % 3
            message = {
                0: "draws :|",
                1: "WINS! :)",
                2: "loses :(",
            }[outcome]
            print(f"Player {j} played {RPS(moves[j]).name:10} and {message}")
            p.procedures.done(i, moves[j], moves[1 - j])

        print()
