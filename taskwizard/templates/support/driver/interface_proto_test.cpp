#include "interface_proto.h"
#include <iostream>

using namespace interface_proto;

int main() {
    data_block<> empty { };
    data_block<int> single { 4 };
    data_block<int, int, int> three { 4, 5, 6 };
    
    call(std::cout, "test", 5, 6, "bla");
}
