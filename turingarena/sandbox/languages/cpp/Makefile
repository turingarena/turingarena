# Makefile for C sandbox

CC=gcc
CFLAGS=-O3 -Wall -Wextra -pedantic

sandbox.o: sandbox.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f sandbox.o 

.PHONY: clean
