YES = 1
NO = 0

def are_coprime(a, b, give_divisor, give_multipliers):
    assert a > 0 and b > 0
    max_div = 1
    for i in range(2,a+b):
        if a%i == 0 and b%i == 0:
            max_div = i
    if max_div > 1:
        give_divisor(max_div)
        return NO
    else:
        for y in range(a):
            if (a*b+max_div - y*b) % a == 0:
                give_multipliers((max_div - y*b) / a, y)
                return YES
    # max_div = xa + yb con |x|<b e |y|<a con xy <= 0
    # -> ab + max_div = xa +yb con x,y >= 0, x<b e y<a

