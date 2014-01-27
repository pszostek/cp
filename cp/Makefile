all: _xed.so xed_disass

xed_disass: xed_disass.c xed_disass.h
	gcc -g -std=c99 -o xed_disass xed_disass.c -Iinclude -L../lib -lxed

xed_bb_chop: xed_bb_chop.c xed_disass.h
	gcc -g -std=c99 -o xed_bb_chop xed_bb_chop.c -Iinclude -L../lib -lxed

xed_bb_chop2: xed_bb_chop2.c xed_disass.h
	gcc -g -std=c99 -o xed_bb_chop2 xed_bb_chop2.c -Iinclude -L../lib -lxed

_xed.so: xed_disass.c xed_wrap.c xed_disass.h
	gcc -fPIC -std=c99 xed_disass.c xed_wrap.c -I/usr/include/python2.7 -L../lib -lxed -shared -o _xed.so

xed_wrap.c: xed.i
xed.py: xed.i _xed.so
	swig -Dinline= -Wall -python xed.i	 

xed-ex1: xed-ex1.o
	g++  -fopenmp  -o xed-ex1 xed-ex1.o ../lib/libxed.a

xed-ex1.o: xed-ex1.cpp
	g++ -fopenmp -I../include -c xed-ex1.cpp	

xed-ex2: xed-ex2.o
	g++  -fopenmp  -o $@ @< ../lib/libxed.a

xed-ex2.o: xed-ex2.cpp
	g++ -fopenmp -I../include -c @<	

.PHONY: clean

clean:
	rm -rf xed-ex2 xed-ex2.o xed_wrap.c _xed.so xed.py *.pyc *.o
