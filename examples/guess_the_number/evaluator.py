import random

from turingarena import *

N = 100

algorithm = submitted_algorithm()


def main():
    # simply random
    for _ in range(10):
        correct = random.randint(1, N)
        is_correct_answer, number_of_guess = compute_fixed(correct)
        if is_correct_answer:
            print('correct, number of guess', number_of_guess)
        else:
            print('WRONG!')

    # move the solution in the most difficult position
    for _ in range(10):
        is_correct_answer, number_of_guess = compute_moving()
        if is_correct_answer:
            print('correct, number of guess', number_of_guess)
        else:
            print('WRONG!')


def compute_fixed(correct):
    with algorithm.run() as process:

        number_of_guess = 0

        def guess(n):
            nonlocal number_of_guess, correct  # clusure with local variable
            number_of_guess += 1
            if n == correct:
                return 0  # correct
            elif n < correct:
                return -1  # too low
            else:
                return 1  # too high

        player_answer = process.functions.play(N, guess=guess)
        return player_answer == correct, number_of_guess


def compute_moving():
    with algorithm.run() as process:
        number_of_guess = 0
        min_value, max_value = 1, N

        def guess(n):
            nonlocal number_of_guess, min_value, max_value  # closure
            number_of_guess += 1
            if min_value == max_value and n == min_value:
                return 0  # correct, only a single possibility
            elif n < min_value or (n - min_value) <= (max_value - n):
                min_value = max(min_value, n + 1)
                return -1  # too low
            elif n > max_value or (n - min_value) > (max_value - n):
                max_value = min(max_value, n - 1)
                return 1  # too high

        player_answer = process.functions.play(N, guess=guess)
        return min_value == max_value and player_answer == min_value, number_of_guess


main()
