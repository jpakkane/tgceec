#include<variant.hpp>

void foo() {
    boost::variant<int> foo;
    boost::variant<boost::variant<char*>> bar;
    foo = bar;
}
