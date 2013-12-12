#!/usr/bin/env python

import xed
import elf
import disass

e = elf.ELFFile("/home/paszoste/cp/tests/files/test_elf")

for section in e.iter_sections():
    print section.name

for function in e.iter_functions():
    print function

for symbol in e.iter_symbols():
    print symbol.name, symbol.entry

fav_num_text = e.get_symbol_text('_ZN6Person14favoriteNumberEv')
fav_num_inst = xed.disassemble_x64(fav_num_text)

# slices, indexing
print fav_num_inst[0]
print type(fav_num_inst[0:5])
print len(fav_num_inst)
print fav_num_inst[-1]

# various mnemonics, instruction class, category
inst = fav_num_inst[0]
inst.get_mnemonic()
inst.get_mnemonic_intel()
inst.get_mnemonic_att()
inst.get_iclass()
inst.get_category()

# get bb starting from given offset, objdump will report 0x40081c
bb = disass.get_basic_block(e, 0x81c)
print len(bb)

# iteration over a list of instructions
for inst in bb:
    print inst, disass.bytes_to_string(inst.get_bytes())
    # these bytes are sometimes corrupted for an uknown reason

# get a list of bb's starting at given offsets
bbs = disass.get_basic_blocks(e, [0x81c, 0x97a, 0x902, 0x832])
assert(isinstance(bbs, list))
assert(isinstance(bbs[0], xed.inst_list_t))
