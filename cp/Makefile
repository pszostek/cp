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
	rm xed-ex2 xed-ex2.o
