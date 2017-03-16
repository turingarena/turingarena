#include <tuple>
#include <iostream>

namespace interface_proto {

template<typename... Types>
struct data_block {

};

template<typename Head, typename... Tail>
struct data_block<Head, Tail...> : data_block<Tail...> {
    Head head;

    data_block<Head, Tail...>(Head _head, Tail... _tail)
            : head(_head), data_block<Tail...>(_tail...)
            {}
};

template<>
struct data_block<> {};

template<typename Head, typename... Tail>
std::ostream& operator<<(std::ostream& os, data_block<Head, Tail...> data) {
    return os << data.head << " " << (data_block<Tail...>) data;
}

template<typename Only>
std::ostream& operator<<(std::ostream& os, data_block<Only> data) {
    return os << data.head << std::endl;
}

std::ostream& operator<<(std::ostream& os, data_block<> data) {
    return os;
}

template<typename... Types>
int call(std::ostream& os, std::string name, Types... parameters) {
    os << name << std::endl;
    os << data_block<Types...>(parameters...);
}

} // namespace interface_proto
