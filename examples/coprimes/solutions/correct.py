# Constant declarations
YES = 1
NO = 0

def recEuclide(a,b):
"""returns the triple [d,x,y] where:
       d is the greatest divisor of a and b;
       x and y are integers such that  xa + yb = d.
"""    
    assert a >= 0 and b >= 0 and a + b > 0
    if b > a:
        answ =  recEuclide(b,a)
        return [ answ[0], answ[2], answ[1] ]
    assert a >= b >= 0 and a > 0    
    if b == 0 or a == b:
        return [a, 1, 0]
    A = a
    q = A // b
    a = A % b
    answ =  recEuclide(a,b)
#        A = bq + a
#        xa + yb = 1
#        xA +(y-xq)b= xbq + xa +yb -xqb
    return [ answ[0], answ[1], answ[2]-answ[1]*q ]


def are_coprime(a, b, give_divisor, give_multipliers):
    assert a > 0 and b > 0
    answ = recEuclide(a,b)
    if answ[0] == 1:
        give_multipliers(answ[1], answ[2])
        return YES
    else:
        give_divisor(answ[0])
        return NO

