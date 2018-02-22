# Makefile for compiling test programs 

CC=gcc
CXX=g++
CFLAGS=-O0
CXXFLAGS=-O0
TESTS=test_read test_constructor test_c_valid test_c_invalid test_cpp_valid test_cpp_invalid 
SANDBOX_OBJECT=../sandbox.o 

all: $(TESTS)

$(SANDBOX_OBJECT): 
	$(MAKE) -C ../ $<

%: %.c $(SANDBOX_OBJECT)
	$(CC) $(CFLAGS) -o $@ $(SANDBOX_OBJECT) $< 

%: %.cpp $(SANDBOX_OBJECT)
	$(CXX) $(CXXFLAGS) -o $@ $(SANDBOX_OBJECT) $< 

clean: 
	rm -f $(TESTS)

.PHONY: all clean 
