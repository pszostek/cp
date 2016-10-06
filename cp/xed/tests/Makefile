#all: xed_disass_test xed_bb_chop_test xed_bb_chop_test2
all: xed_disass_test xed_bb_chop_test3 xed_bb_chop_test3_debug

tests:
		./run.sh

xed_disass_test: ../xed_disass.c ../xed_disass.h xed_disass_test.c
		gcc -ggdb -O3 -std=c99 -o xed_disass_test ../xed_disass.c xed_disass_test.c -I../../include -I.. -L../../../lib -lxed

#xed_bb_chop_test: ../xed_bb_chop.cxx ../xed_disass.h ../xed_bb_chop.h xed_bb_chop_test.cxx ../xed_disass.c
#		g++ -O3 -std=c++11 -ftree-vectorize -g ../xed_disass.c ../xed_bb_chop.cxx xed_bb_chop_test.cxx -I.. -I../../include -L../../../lib -lxed -o xed_bb_chop_test

xed_bb_chop_test3: ../xed_bb_chop.cxx ../xed_disass.h ../xed_bb_chop.h xed_bb_chop_test3.cxx ../xed_disass.c
		g++ -ggdb -O3 -std=c++11 -ftree-vectorize ../xed_disass.c ../xed_bb_chop.cxx xed_bb_chop_test3.cxx -I.. -I../../include -L../../../lib -lxed -o xed_bb_chop_test3

xed_bb_chop_test3_debug: ../xed_bb_chop.cxx ../xed_disass.h ../xed_bb_chop.h xed_bb_chop_test3.cxx ../xed_disass.c
		g++ -ggdb -O0 -std=c++11 -ftree-vectorize ../xed_disass.c ../xed_bb_chop.cxx xed_bb_chop_test3.cxx -I.. -I../../include -L../../../lib -lxed -o xed_bb_chop_test3_debug

.PHONY: clean

clean:
#	rm -f xed_disass_test xed_bb_chop_test xed_bb_chop_test2
	rm -f xed_disass_test xed_bb_chop_test3
