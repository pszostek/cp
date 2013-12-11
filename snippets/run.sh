make
python fun_list.py -s ../test_elf
python fun_list.py -t /bin/ls > ls.text
./xed-ex1 64 ./ls.text
