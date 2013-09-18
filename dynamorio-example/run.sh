#!/usr/bin/env bash

if [ -z "$(which drrun)" ]; then
	echo "drrun not in the PATH"
	exit 1
fi 

make
CURDIR=$(pwd)
cd $(dirname $(which drrun))
./drrun -c $CURDIR/libbbcount.so -- $CURDIR/../test_elf
cd $CURDIR
