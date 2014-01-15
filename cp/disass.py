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
                                 XED_ICLASS  XED_ISA_SET  XED_CATEGORY 
dso_name  bb_offset inst_offset                                          
libc.so.6 312       0              1.073849    -1.042593      0.602416   
                    1              0.988712    -1.896690     -0.260631   
                    4             -1.014164    -0.030036      0.350817   
                    6             -0.515853    -0.696777      0.777544   
                    7             -0.910810    -0.366494      0.841812   
                    3             -0.470408     0.321503      0.954833 
    """
    import pandas as pd
    result_list = []
    prev_dso_path = None
    for dso_path, offset_list in bb_dict.items():
        if prev_dso_path != dso_path:
            elffile = elf.ELFFile(dso_path)
        for offset in offset_list:
            bb = get_basic_block(elffile, offset)
            offset_inside_bb = 0
            for inst in bb:
                inst_length = inst.get_length()
                result_list.append((dso_path,
                                    offset,
                                    offset_inside_bb,
                                    inst.get_iclass_code(),
                                    inst.get_isa_set_code(),
                                    inst.get_category_code()))
                offset_inside_bb += inst_length
        prev_dso_path = dso_path
    return pd.DataFrame


def get_basic_block(module, offset):
    assert isinstance(module, elf.ELFFile)
    fd = module._fd

    section = module.get_section_by_offset(offset)
    section_offset = section.header['sh_offset']
    section_size = section.header['sh_size']
    section_end = section_size + section_offset

    to_be_read = section_end - offset
    #bytes = fd.read(to_be_read)
    chunk_size = 64 
    while True:
        fd.seek(offset)
        bytes = fd.read(chunk_size)
        bb = disassemble_x64_until_bb_end(bytes, base=offset)
        if not bb.is_finished_by_branch():
            chunk_size *= 2
        else:
            return bb 
    # cur = offset

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
