class Solution extends Skeleton {
// Constant declarations
private static final YES = 1;
private static final NO = 0;


    // interface are_coprime_callbacks {
    //     void give_divisor(int d);
    //     void give_multipliers(int x, int y);
    // }

    int are_coprime(int a, int b, are_coprime_callbacks callbacks) {
	assert(a > 0); assert(b > 0);
	int  max_div = 1;
	for(int i= 2; i<a+b; i++)
	    if(a%i == 0 && b%i == 0)
		max_div = i;
	if(max_div > 1) {
	    callbacks.give_divisor(max_div);
	    return NO;
	}
	for(int y = 0; y<a; y++)
	    if( (a*b+max_div - y*b) % a == 0) {
		callbacks.give_multipliers((max_div - y*b) / a, y);
		return YES;
	    }
	// max_div = xa + yb con |x|<b e |y|<a con xy <= 0
	// -> ab + max_div = xa +yb con x,y >= 0, x<b e y<a
    }
}
