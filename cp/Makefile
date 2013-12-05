_disass.so: xed_disass.c disass_wrap.c xed_disass.h
	gcc -fPIC xed_disass.c disass_wrap.c -I/usr/include/python2.7 -L../lib -lxed -shared -o _disass.so

disass.py: disass.i _disass.so
	swig -Wall -python disass.i	 

disass_wrap.c: disass.i
	swig -Wall -python disass.i
	 

all: xed-ex1 xed-ex2

xed-ex1: xed-ex1.o
	g++  -fopenmp  -o xed-ex1 xed-ex1.o ../lib/libxed.a

xed-ex1.o: xed-ex1.cpp
	g++ -fopenmp -I../include -c xed-ex1.cpp	

xed-ex2: xed-ex2.o
	g++  -fopenmp  -o xed-ex2 xed-ex2.o ../lib/libxed.a

xed-ex2.o: xed-ex2.cpp
	g++ -fopenmp -I../include -c xed-ex2.cpp	

.PHONY: clean

clean:
	rm -rf xed-ex2 xed-ex2.o disass_wrap.c _disass.so disass.py *.pyc *.o
