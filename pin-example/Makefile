bbcount.so: bbcount.o
	g++ -shared -Wl,--hash-style=sysv -Wl,-Bsymbolic -Wl,--version-script=include/pin/pintool.ver -o bbcount.so bbcount.o  -Llib -L../../../extras/xed2-intel64/lib -lpin -lxed -ldwarf -lelf -ldl

bbcount.o: bbcount.cpp
	g++ -DBIGARRAY_MULTIPLIER=1 -DUSING_XED -Wall -Werror -Wno-unknown-pragmas -fno-stack-protector -DTARGET_IA32E -DHOST_IA32E -fPIC -DTARGET_LINUX  -Iinclude/util -Iinclude/pin -Iinclude/pin/gen -Iinclude -O3 -fomit-frame-pointer -fno-strict-aliasing -std=gnu++11 -std=gnu++0x -o bbcount.o -c bbcount.cpp
