#include <cassert>

const int YES = 1;
const int NO = 0;

void recEuclide(int a, int b, int answ[3]) {
  /* returns the answ array [d,x,y] where:
       d is the greatest divisor of a and b;
       x and y are integers such that  xa + yb = d.
  */  
  assert(a >= 0); assert(b >= 0); assert(a + b > 0);
  if(b > a) {
    int rec_answ[3];
    recEuclide(b,a, rec_answ);
    answ[0] = rec_answ[0]; answ[1] = rec_answ[2]; answ[2] = rec_answ[1];
    return;
  }
  assert(a >= b); assert(b >= 0); assert(a > 0);    
  if( (b == 0) || (a == b) ) {
    answ[0] = a; answ[1] = 1; answ[2] = 0;
    return;
  }    
  int A = a;
  int q = A / b;
  a = A % b;
  int rec_answ[3];
  recEuclide(a,b, rec_answ);
  //    A = bq + a
  //    xa + yb = 1
  //    xA +(y-xq)b= xbq + xa +yb -xqb
  answ[0] = rec_answ[0]; answ[1] = rec_answ[1]; answ[2] = rec_answ[2]-rec_answ[1]*q;
}

int are_coprime(int a, int b, void give_divisor(int d), void give_multipliers(int x, int y)) {
  assert(a > 0); assert(b > 0);
  int answ[3];
  recEuclide(a,b, answ);
  if(answ[0] == 1) { 
    give_multipliers(answ[1], answ[2]);
    return YES;
  }  
  else {
    give_divisor(answ[0]);
    return NO;
  }
}
