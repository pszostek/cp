xed-ex2: xed-ex2.o
	g++    -o xed-ex2 xed-ex2.o ../lib/libxed.a

xed-ex2.o: xed-ex2.cpp
	g++ -I../include -c xed-ex2.cpp	

.PHONY: clean

clean:
	rm xed-ex2 xed-ex2.o
