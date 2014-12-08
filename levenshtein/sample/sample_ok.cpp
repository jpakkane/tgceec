#include<iostream>
#include<fstream>
#include<sstream>

int main(int /*argc*/, char **argv) {
    std::ifstream t(argv[1]);
    std::stringstream s;
    s << t.rdbuf();
    auto i = s.str();
    std::string j(i.rbegin(), i.rend());
    std::ofstream o(argv[2]);
    o << j;
    return 0;
 }
