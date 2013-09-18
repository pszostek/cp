libbbcount.so: bbcount.o
	g++ -shared bbcount.o -o libbbcount.so

bbcount.o: bbcount.cpp
	g++ -c bbcount.cpp -fPIC -DLINUX -DX86_64 -o bbcount.o -Iinclude
