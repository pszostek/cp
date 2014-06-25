
#include <iostream>

namespace some_namespace {
class Shape
{
protected:
    float width, height;
public:
    void set_data (float a, float b)
    {
        width = a;
        height = b;
    }
    int some_function() {
    }
};

class Rectangle: public Shape
{
public:
    float area ()
    {
        return (width * height);
    }
    float perimeter() {
    }
};

class Triangle: public Shape
{
public:
    float area ()
    {
        return (width * height / 2);
    }
    float perimeter() {
    }
};
}

int main ()
{
    using namespace some_namespace;
    using namespace std;
    Rectangle rect;

    Triangle tri;
    rect.set_data (5,3);
    tri.set_data (2,5);
    tri.some_function();
    cout << rect.area() << endl;
    cout << tri.area() << endl;
    cout << tri.perimeter() << endl;
    cout << rect.perimeter() << endl;
    return 0;
}

