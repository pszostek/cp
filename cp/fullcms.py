#!/usr/bin/env python

import timeit

def mean(lst):
    return sum(lst)/len(lst)

# setup='''
# import xed
# import disass
# import elf

# e = elf.ELFFile("../real_data/fullcms")
# offsets = [int(line.strip(), 16)-0x400000 for line in open("../real_data/pawel.fullcms").readlines()]
# '''

# #t = timeit.Timer(stmt="disass.get_basic_blocks(e, offsets)", setup=setup)
# t = timeit.Timer(stmt="output=disass.get_inst_lists_for_basic_blocks({'../real_data/fullcms':offsets})", setup=setup)

# print "mean time over %d runs: %fs" % (3, mean(t.repeat(3, 1)))



import xed
import disass
import elf

e = elf.ELFFile("../real_data/fullcms")
offsets = [int(line.strip(), 16)-0x400000 for line in open("../real_data/pawel.fullcms").readlines()]

output=disass.get_inst_lists_for_basic_blocks({"../real_data/fullcms":offsets})
output.to_csv('fullcms.csv')
print disass.get_source_location({"../real_data/fullcms":offsets})
