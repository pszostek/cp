#!/usr/bin/env bash

if [ -z $(which pin) ]; then
	echo "pin not found in the PATH"
	exit 1
fi

make
pin -t bbcount.so -- ../test_elf
echo ""
echo "Have a look at bbcount.out."

