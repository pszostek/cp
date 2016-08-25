#!/usr/bin/env bash
make -C cp tests
python -m cp.elf.elffile_test
