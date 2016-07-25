all: xed.py _xed.so tests

tests:
	$(MAKE) -C tests

_xed.so: xed_disass.c xed_wrap.cxx xed_disass.h
	g++ -fPIC xed_disass.c xed_wrap.cxx xed_bb_chop.cxx -I/usr/include/python2.6 -I. -I.. -I../include -L../../lib -lxed -shared -o _xed.so

xed_wrap.cxx xed.py: xed.i
	swig -I.. -I../include -Dinline= -Wall -classic -python -c++ xed.i	 

xed-ex1: xed-ex1.o
	g++  -fopenmp  -o xed-ex1 xed-ex1.c ../lib/libxed.a

xed-ex2: xed-ex2.o
	g++  -fopenmp  -o $@ @< ../lib/libxed.a

xed-ex2.o: xed-ex2.cpp
	g++ -fopenmp -I../include -c @<	

.PHONY: clean tests

clean:
	rm -rf xed-ex2 xed-ex2.o xed_wrap.cxx _xed.so xed.py *.pyc *.o xed_bb_chop
	$(MAKE) -C tests clean
