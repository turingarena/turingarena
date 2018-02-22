# Makefile for C sandbox

CC=gcc
CFLAGS=-O3 -Wall -Wextra -pedantic
TESTDIR=test/
SANDBOX_OBJECT=sandbox.o

all: $(SANDBOX_OBJECT)

$(SANDBOX_OBKECT): sandbox.c
	$(CC) $(CFLAGS) -c -o $@ $<

clean: clean_tests
	rm -f $(SANDBOX_OBJECT) 

clean_tests:
	$(MAKE) -C $(TESTDIR) clean 

tests: $(SANDBOX_OBJECT) 
	$(MAKE) -C $(TESTDIR) all

.PHONY: all clean tests clean_tests
