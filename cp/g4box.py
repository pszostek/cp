#!/usr/bin/env python

# import timeit

# setup='''
# import xed
# import disass
# import elf

# e = elf.ELFFile("../testG4Box")
# offsets = [int(line.strip()) for line in open("../pawel.g4box.txt").readlines()]
# '''

#t = timeit.Timer(stmt="disass.get_basic_blocks(e, offsets)", setup=setup)
# t = timeit.Timer(stmt="disass.get_inst_lists_for_basic_blocks({'../testG4Box':offsets})", setup=setup)
# print t.repeat(3, 1)



import xed
import disass
import elf
import pandas

e = elf.ELFFile("../real_data/testG4Box")
offsets = [int(line.strip()) for line in open("../real_data/pawel.g4box.txt").readlines()]

print len(offsets)
# bbs = disass.get_basic_blocks(e, offsets)
# for idx, bb in enumerate(bbs):
#     print len(bb), hex(offsets[idx])
output=disass.get_inst_lists_for_basic_blocks({"../real_data/testG4Box":offsets})
print output.head(50)