all: _xed.so xed_bb_chop_test

xed_disass_test: xed_disass.c xed_disass.h xed_disass_test.c
	gcc -g -std=c99 -o xed_disass_test xed_disass.c xed_disass_test.c -I../include -L../../lib -lxed

xed_bb_chop: xed_bb_chop.c xed_disass.h
	gcc -g -std=c99 -o xed_bb_chop xed_bb_chop.c -I../include -L../../lib -lxed

xed_bb_chop2: xed_bb_chop2.c xed_disass.h
	gcc -O3 -ftree-vectorize -g -DDEBUG -std=c99 -o xed_bb_chop2 xed_bb_chop2.c -I../include -L../../lib -lxed

xed_bb_chop_test: xed_bb_chop.cxx xed_disass.h xed_bb_chop.h xed_bb_chop_test.cxx xed_disass.c
	g++ -O3 -ftree-vectorize -g xed_disass.c xed_bb_chop.cxx xed_bb_chop_test.cxx -I../include -L../../lib -lxed -o xed_bb_chop_test

xed_bb_chop2_debug: xed_bb_chop2.c xed_disass.h
	gcc -O3 -ftree-vectorize -DDEBUG -g -std=c99 -o xed_bb_chop2_debug xed_bb_chop2.c -I../include -L../../lib -lxed

_xed.so: xed_disass.c xed_wrap.c xed_disass.h
	g++ -fPIC xed_disass.c xed_wrap.c xed_bb_chop.cxx -I/usr/include/python2.7 -I. -I.. -I../include -L../../lib -lxed -shared -o _xed.so

xed_wrap.c: xed.i
	swig -I.. -I../include -Dinline= -Wall -python xed.i

xed.py: xed.i _xed.so
	swig -I.. -I../include -Dinline= -Wall -python xed.i	 


xed-ex1: xed-ex1.o
	g++  -fopenmp  -o xed-ex1 xed-ex1.c ../lib/libxed.a

xed-ex2: xed-ex2.o
	g++  -fopenmp  -o $@ @< ../lib/libxed.a

xed-ex2.o: xed-ex2.cpp
	g++ -fopenmp -I../include -c @<	

.PHONY: clean

clean:
	rm -rf xed-ex2 xed-ex2.o xed_wrap.c _xed.so xed.py *.pyc *.o xed_bb_chop2 xed_bb_chop3
