CXXFLAGS=-std=c++14

all: arena

scanner.cpp: scanner.l parser.hpp
	flex -o $@ $<

parser.hpp: parser.cpp

parser.cpp: parser.y
	bison -o $@ $<

arena: scanner.o parser.o model.o arena.cpp

clean:
	rm *.o arena parser.cpp parser.hpp scanner.cpp location.hh stack.hh
