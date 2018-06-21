from turingarena import *

NUMBER_OF_MATCH = 100


def pos_to_yx(pos):
    return pos // 3, pos % 3


def yx_to_pos(y, x):
    return y * 3 + x


print("running game")

with algorithm.run(global_variables=dict(
        position_mapping=[[0, 1, 2], [3, 4, 5], [6, 7, 8]]
)) as p:
    memory_usage = p.sandbox.get_info().memory_usage
    print(f"Memory usage: {memory_usage} bytes")

    number_of_match = NUMBER_OF_MATCH
    result = p.functions.play_first_round()
    print(result, pos_to_yx(result))

#
#        number_of_match = None
#        number_of_match = NUMBER_OF_MATCH
#
#        for i in range(number_of_match):
#
#            first_turn_for_player = result = continue_match = None
#
#            p.procedures.start_new_game()
#
#            first_turn_for_player = random.randint(0,1)
#
#            if first_turn_for_player:
#                result = p.functions.play_first_round()
#
#            continue_match = True
#            for i in range(4):
#                if continue_match:
#                    result = p.functions.play_a_round(
#                            random.randint(0,2), random.randint(0,2))
#                    continue_match = True
