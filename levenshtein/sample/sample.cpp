#include<iostream>
#include<fstream>
#include<sstream>
using namespace std;
int main(int, char **argv) {
ifstream t(argv[1]);
stringstream s;
s << t.rdbuf();
auto i = s.str();
string j(i.rbegin(), i.rend());
ofstream o(argv[2]);
o << j;
return 0
}
