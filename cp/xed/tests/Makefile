all: xed_disass_test xed_bb_chop_test

xed_disass_test: ../xed_disass.c ../xed_disass.h xed_disass_test.c
		gcc -g -Wall -std=c99 -o xed_disass_test ../xed_disass.c xed_disass_test.c -I../../include -I.. -L../../../lib -lxed

xed_bb_chop_test: ../xed_bb_chop.cxx ../xed_disass.h ../xed_bb_chop.h xed_bb_chop_test.cxx ../xed_disass.c
		g++ -O3 -Wall -std=c++11 -ftree-vectorize -g ../xed_disass.c ../xed_bb_chop.cxx xed_bb_chop_test.cxx -I.. -I../../include -L../../../lib -lxed -o xed_bb_chop_test

.PHONY: clean

clean:
	rm -f xed_disass_test xed_bb_chop_test
