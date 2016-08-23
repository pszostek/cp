#!/bin/bash

# this script extracts the current kernel version and system.map

# https://en.wikipedia.org/wiki/System.map - a guide to symbol types.
#	filtering out absolute and data symbols (these are prime suspects
#	as they fall out of the 0xfff ... address range we will be looking at

ME=$(readlink -f "$0")
MYPATH=$(dirname "$ME")

$MYPATH/extract-vmlinux.sh /boot/vmlinuz-`uname -r` > /tmp/vmlinux.elf
cat /boot/System.map-`uname -r` | grep -v " A " | grep -v " D " | grep -v " d " | sort > /tmp/vmlinux.symbols
# the above line might just become ' | grep fffffff ' in the future
return 0 # todo: return failure when needed

