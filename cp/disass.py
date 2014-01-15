#!/usr/bin/env python

import xed
import elf

def bytes_to_string(bytes):
    return ' '.join(map(lambda x: '%02x' % ord(x), bytes))

def disassemble_x86(data, base=0):
    assert isinstance(data, basestring)
    return xed._disassemble_x86(data, base)

def disassemble_x64(data, base=0):
    assert isinstance(data, basestring)
    return xed._disassemble_x64(data, base)

def disassemble_x64_until_bb_end(data, base=0):
    assert isinstance(data, basestring)
    return xed._disassemble_x64_until_bb_end(data, base)

def get_inst_lists_for_basic_blocks(bb_dict):
    """ Function that disassembles basic blocks at given offsets

    bb_list: a dictionary containing pairs of DSO paths and lists of offsets to be disassembled
    returns a pandas.DataFrame containing disassembled instructions in rows and indexed by DSO path and BB offset
        for instance:
                                  inst_length   XED_ICLASS  XED_ISA_SET  XED_CATEGORY 
dso_name  bb_offset inst_offset                                          
libc.so.6 312       0                   1           1           1             6   
                    1                   3           0           5             2   
                    4                   4           23          7             3   
                    6                   3           43          3             7   
                    7                   3           54          4             8   
                    3                   4           56          2             9 
    """
    import pandas as pd
    import numpy
    result_list = []
    prev_dso_path = None
    index_tuples = []
    for dso_path, offset_list in bb_dict.items():
        if prev_dso_path != dso_path:
            elffile = elf.ELFFile(dso_path)
        for bb_offset in offset_list:
            bb = get_basic_block(elffile, bb_offset)
            offset_inside_bb = 0
            for inst in bb:
                inst_length = inst.get_length()
                index_tuples.append((dso_path,
                                    bb_offset,
                                    offset_inside_bb))
                result_list.append((inst_length,
                                    inst.get_iclass(),
                                    inst.get_isa_set(),
                                    inst.get_category(),
                                    xed.xed_decoded_inst_noperands(inst)))
                offset_inside_bb += inst_length
        prev_dso_path = dso_path
    index = pd.MultiIndex.from_tuples(index_tuples, names=['dso_path',
                                                           'bb_offset',
                                                           'inst_offset'])
    ret_data_frame = pd.DataFrame(result_list,
                                  index=index,
                                  columns=['inst_length',
                                           'XED_ICLASS',
                                           'XED_ISA_SET',
                                           'XED_CATEGORY',
                                           'noperands'])
    return ret_data_frame


def get_basic_block(module, offset):
    assert isinstance(module, elf.ELFFile)
    fd = module._fd

    section = module.get_section_by_offset(offset)
    section_offset = section.header['sh_offset']
    section_size = section.header['sh_size']
    section_end = section_size + section_offset

    chunk_size = 64 
    while True:
        fd.seek(offset)
        bytes = fd.read(chunk_size)
        bb = disassemble_x64_until_bb_end(bytes, base=offset)
       # print('base %d, ifbb %d' % (bb.base, bb.is_finished_by_branch()))
        if bb.size == 0:
            chunk_size *= 2
        elif not bb.is_finished_by_branch():
            chunk_size += 2
        else:
            return bb 

    # ret = xed.inst_list_t()
    # while cur < section_end:
    #     print "iteration"
    #     if cur + chunk_size > section_end:
    #         bytes = fd.read(section_end-cur)
    #     else:
    #         bytes = fd.read(chunk_size)
    #     bb = disassemble_x64_until_bb_end(bytes, base=cur)
    #   #  ret.extend(bb)
    #     cur += chunk_size
    # return ret

def get_basic_blocks(module, offset_list):
    assert isinstance(offset_list, list)
    ret = []
    for offset in offset_list:
        ret.append(get_basic_block(module, offset))
    return ret

if __name__ == "__main__":
    e = elf.ELFFile("/home/paszoste/cp/tests/files/test_elf")
    bb = get_basic_block(e, 0x81f)
    for inst in bb:
        print inst.get_mnemonic_intel(), inst.get_length(), inst.get_operand_width(), inst.get_number_of_operands(), bytes_to_string(inst.get_bytes())
