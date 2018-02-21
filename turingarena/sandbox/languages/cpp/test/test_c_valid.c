#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() 
{
	/* io test */
	printf("Hello, world!"); 

	/* small memory allocation test (10Mb) */
	char *small = malloc(10 * 1000);
	memset(small, 42, 10 * 1000);

	/* big memory allocation test (1Gb) */
	char *big = malloc(1000 * 1000);
	memset(big, 42, 1000 * 1000);

	/* memory deallocation test */
	free(small);
	free(big);

	/* exit test */
	exit(EXIT_SUCCESS);
}