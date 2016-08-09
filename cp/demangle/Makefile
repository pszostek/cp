all: demangle.py _demangle.so

_demangle.so: demangle.h demangle_wrap.c
	    gcc -fPIC demangle_wrap.c -I/usr/local/include/python2.7 -I. -I.. -I../include -L../../lib -liberty -shared -o _demangle.so

demangle_wrap.c demangle.py: demangle.i
	    swig -I.. -I../include -Dinline= -Wall -python demangle.i

.PHONY: clean tests

clean:
	    rm -rf  demangle_wrap.c _demangle.so demangle.py *.pyc *.o
