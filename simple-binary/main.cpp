
#include <iostream>
#include <string>

namespace nmsp1 {

class A {
    public:
        std::string member() {
            return "adfadf";
        }
        int member2() {
            return 42;
        }
};

class B {
    public:
        std::string member() {
            return "adfadf";
        }
        int member2() {
            return 42;
        }
};
}

namespace nmsp2 {

int function1() {
    return 3;
}

int function1(int a) {
    return a;
}
}
int main() {
    nmsp1::A a;
    a.member();
    a.member2();

    nmsp1::B b;
    b.member();
    b.member2();
    return 0;
}



