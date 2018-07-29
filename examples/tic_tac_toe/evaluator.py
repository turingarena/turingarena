from turingarena import submission, run_algorithm, evaluation, AlgorithmRuntimeError

import random

NUMBER_OF_MATCH = 100

EMPTY = 0
PLAYER = 1
OPPONENT = 2


def print_grid(grid):
    print(f" {grid[0][0]} | {grid[0][1]} | {grid[0][2]}")
    print("---+---+---")
    print(f" {grid[1][0]} | {grid[1][1]} | {grid[1][2]}")
    print("---+---+---")
    print(f" {grid[2][0]} | {grid[2][1]} | {grid[2][2]}")


def find_winner(grid):
    result = None
    grid = grid[0] + grid[1] + grid[2]
    if grid[0]==grid[1] and grid[1]==grid[2] and grid[0]!=' ': result = grid[0]
    if grid[3]==grid[4] and grid[4]==grid[5] and grid[3]!=' ': result = grid[3]
    if grid[6]==grid[7] and grid[7]==grid[8] and grid[6]!=' ': result = grid[6]
    if grid[0]==grid[3] and grid[3]==grid[6] and grid[0]!=' ': result = grid[0]
    if grid[1]==grid[4] and grid[4]==grid[7] and grid[1]!=' ': result = grid[1]
    if grid[2]==grid[5] and grid[5]==grid[8] and grid[2]!=' ': result = grid[2]
    if grid[0]==grid[4] and grid[4]==grid[8] and grid[4]!=' ': result = grid[4]
    if grid[6]==grid[4] and grid[4]==grid[2] and grid[4]!=' ': result = grid[4]

    # check if draw
    if result is None:
        for x in grid:
            if x == ' ':
                return None
        return 'D'
    else:
        return result


def play_round(player, symbol, grid):
    new_grid = [[0 for _ in range(3)] for _ in range(3)]

    for y in range(3):
        for x in range(3):
            if grid[y][x] == ' ':
                new_grid[y][x] = EMPTY
            elif grid[y][x] == symbol:
                new_grid[y][x] = PLAYER
            else:
                new_grid[y][x] = OPPONENT

    placed = False
    def place(y, x):
        nonlocal placed
        if placed:
            raise RuntimeError("Invalid action: place called multiple times in the same round!")
        placed = True 
        grid[y][x] = symbol    

    player.procedures.play_move(new_grid, callbacks=[place])   


def run_match():
    with run_algorithm(submission.player1) as p1, run_algorithm(submission.player2) as p2:
        players = (p1, p2)
        symbols = ('X', 'O')

        grid = [[' ' for _ in range(3)] for _ in range(3)]

        winner = None
        while not winner:
            for player, symbol in enumerate(symbols):
                print(f"Turn of player {player}({symbol})")
                play_round(players[player], symbol, grid)
                print_grid(grid)
                winner = find_winner(grid)
                if winner: 
                    break

        for player in players:
            player.procedures.terminate()

        if winner == 'D':
            print(f"Game is draw")
        else:
            print(f"Player {symbols.index(winner)} ({winner}) won!")

        evaluation.data(dict(result=winner))

        return winner
    

run_match()
exit()
