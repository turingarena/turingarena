#include <iostream>
#include <stdio.h>

using namespace std;

int main() {
	setvbuf(stdout, NULL, _IONBF, 0);
	printf("Test solution\n");
	fprintf(stderr, "sent mess\n");
}
