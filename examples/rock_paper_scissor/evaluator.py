from turingarena import *

n_moves = 10

move_names = {
    0: ("   rock", "\u270a"),
    1: ("  paper", "\u270b"),
    2: ("scissor", "\u270c"),
}

outcome_messages = {
    0: "draws :|",
    1: "wins! :)",
    2: "loses :(",
}

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
            message = outcome_messages[outcome]
            move_name, move_symbol = move_names[moves[j]]
            print(f"    {move_symbol}\t player {j} plays {move_name} and {message}")
            p.procedures.done(i, moves[j], moves[1 - j])
