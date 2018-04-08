import random

N = 100

def evaluate(algorithm):
    for _ in range(10):
        with algorithm.run() as process:

            correct = random.randint(1,N)
            number_of_guess = 0

            def guess(n):
                nonlocal number_of_guess, correct
                number_of_guess += 1
                if n == correct:
                    return 0
                elif n < correct:
                    return -1 # too low
                else:
                    return 1  # too high

            player_answer =  process.call.play(N,guess=guess)

            if player_answer == correct:
                print('correct:',correct,'number of guess:',number_of_guess)
            else:
                print('WRONG!')
