#include <stdlib.h>

int guess(int n);

int play(int n) {
    srand( 123456 );
    int value;
    do { value = rand()%n + 1; } while ( guess(value) != 0 ) ;
    return value;
}
