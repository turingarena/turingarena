#include <stdio.h>

__attribute__((constructor(0))) static void init()
{
	/* should fail */
	FILE *fp = fopen("Makefile", "w");
}

int main() {}