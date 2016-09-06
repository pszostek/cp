#!/usr/bin/env bash
make -C cp tests
python -m cp.elf.elffile_test
python -m cp.elf.disass_test
