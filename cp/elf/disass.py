#!/usr/bin/env python

from xed import xed
import elffile as elffile_mod
import addr2line

def bytes_to_string(bytes):
    return ' '.join(map(lambda x: '%02x' % ord(x), bytes))

def disassemble_x86(data, base=0):
    assert isinstance(data, basestring)
    base = long(base)
    return xed._disassemble_x86(data, base)

def disassemble_x64(data, base=0):
    assert isinstance(data, basestring)
    base = long(base)
    return xed._disassemble_x64(data, base)

def disassemble_x64_until_bb_end(data, base=0):
    assert isinstance(data, basestring)
    base = long(base)
    return xed._disassemble_x64_until_bb_end(data, base)

def get_source_location(bb_dict):
    """ Function that looks for provenance of instruction under given addresses

    bb_dict: a dictionary containing pairs of DSO paths and lists of offsets to be disassembled
    returns a list of tuples (source_file:line) or (None, None) if not known.
    """
    from pandas import MultiIndex, DataFrame
    index_tuples = []
    data_tuples = []
    for dso_path in bb_dict.keys():
        addr2line.initialize_line_numbers(dso_path)
        for offset in bb_dict[dso_path]:
            loc = addr2line.find_line_number(offset+0x400000)
            ret = loc[0]
            source_file_name = loc[1]
            source_file_line = loc[2]
            index_tuples.append((dso_path, offset))
            if ret:
              data_tuples.append((source_file_name, source_file_line))
            else:
              data_tuples.append((None, None))
    index = MultiIndex.from_tuples(index_tuples, names=['dso_path', 'bb_offset'])
    columns = ['source_file', 'line']
    return DataFrame(data_tuples,
                     index=index,
                     columns=columns)

def get_disassembly_for_basic_blocks(bb_dict):
    """ Function that disassembles basic blocks at given offsets and returns disassembly text

    bb_dict: a dictionary containing pairs of DSO paths and lists of offsets to be disassembled
    returns a pandas.DataFrame containing disassembly in rows and indexed by DSO path and BB offset
        for instance:
                                  disassembly 
dso_name  bb_offset inst_offset                                          
libc.so.6 312       0                   1    
                    1                   3   

    """
    assert isinstance(bb_dict, dict)
    from collections import namedtuple
    import pandas as pd
    import numpy
    Operand = namedtuple('Operand', ['type', 'width', 'name', 'action', 'elem'], verbose=False)
    result_list = []
    prev_dso_path = None
    index_tuples = []
    for dso_path, offset_list in bb_dict.items():
        if prev_dso_path != dso_path:
            elffile = elffile_mod.ELFFile(dso_path)
        for bb_offset in offset_list:
            bb = get_basic_block(elffile, bb_offset)
            offset_inside_bb = 0
            for inst in bb:
                index_tuples.append((dso_path,
                                    bb_offset,
                                    offset_inside_bb))
                result_list.append(inst.get_mnemonic_intel())
                offset_inside_bb += inst.get_length()

    index = pd.MultiIndex.from_tuples(index_tuples, names=['dso_path',
                                                           'bb_offset',
                                                           'inst_offset'])
    ret_data_frame = pd.DataFrame(result_list,
                                  index=index,
                                  columns=['disassembly'])
    return ret_data_frame

def get_inst_lists_for_basic_blocks(bb_dict):
    """ Function that disassembles basic blocks at given offsets

    bb_dict: a dictionary containing pairs of DSO paths and lists of offsets to be disassembled
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
    assert isinstance(bb_dict, dict)
    from collections import namedtuple
    import pandas as pd
    Operand = namedtuple('Operand', ['type', 'width', 'name', 'action', 'elem'], verbose=False)
    result_list = []
    prev_dso_path = None
    index_tuples = []
    for dso_path, offset_list in bb_dict.items():
        if prev_dso_path != dso_path:
            elffile = elffile_mod.ELFFile(dso_path)
        for bb_offset in offset_list:
            bb = get_basic_block(elffile, bb_offset)
            offset_inside_bb = 0
            for inst in bb:
                inst_length = inst.get_length()
                noperands = xed.xed_decoded_inst_noperands(inst)
                unaligned = xed.xed_decoded_inst_get_attribute(inst, xed.XED_ATTRIBUTE_UNALIGNED)
                simd_scalar = xed.xed_decoded_inst_get_attribute(inst, xed.XED_ATTRIBUTE_SIMD_SCALAR)
                packed_alignment = xed.xed_decoded_inst_get_attribute(inst, xed.XED_ATTRIBUTE_SIMD_PACKED_ALIGNMENT)
                gather = xed.xed_decoded_inst_get_attribute(inst, xed.XED_ATTRIBUTE_GATHER)
                prefetch = xed.xed_decoded_inst_get_attribute(inst, xed.XED_ATTRIBUTE_PREFETCH)
                scalable = xed.xed_decoded_inst_get_attribute(inst, xed.XED_ATTRIBUTE_SCALABLE)

                inst_inst = xed.xed_decoded_inst_inst(inst)
                operands = []
                for idx in xrange(0,2):
                    if idx >= noperands:
                        operands.append(Operand(None, None, None, None, None))
                    else:
                        xed_op = xed.xed_inst_operand(inst_inst, idx)
                        op = Operand(type=xed.xed_operand_type_enum_t2str(xed.xed_operand_type(xed_op)),
                                     width=xed.xed_operand_width_enum_t2str(xed.xed_operand_width(xed_op)),
                                     name=xed.xed_operand_enum_t2str(xed.xed_operand_name(xed_op)),
                                     action=xed.xed_operand_action_enum_t2str(xed.xed_operand_rw(xed_op)),
                                     elem=xed.xed_operand_element_type_enum_t2str(xed.xed_decoded_inst_operand_element_type(inst, idx)))
                        operands.append(op)
                index_tuples.append((dso_path,
                                    bb_offset,
                                    offset_inside_bb))
                result_list.append((inst_length,
                                    inst.get_iclass(),
                                    inst.get_isa_set(),
                                    inst.get_category(),
                                    inst.get_extension(),
                                    noperands,
                                    unaligned,
                                    simd_scalar,
                                    packed_alignment,
                                    gather,
                                    prefetch,
                                    scalable,
                                    operands[0].type,
                                    operands[0].width,
                                    operands[0].name,
                                    operands[0].action,
                                    operands[0].elem,
                                    operands[1].type,
                                    operands[1].width,
                                    operands[1].name,
                                    operands[1].action,
                                    operands[1].elem))
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
                                           'XED_EXTENSION',
                                           'noperands',
                                           'unaligned',
                                           'simd_scalar',
                                           'packed_alignment',
                                           'gather',
                                           'prefetch',
                                           'scalable',
                                           'op0.type',
                                           'op0.width',
                                           'op0.name',
                                           'op0.action',
                                           'op0.elem',
                                           'op1.type',
                                           'op1.width',
                                           'op1.name',
                                           'op1.action',
                                           'op1.elem'])
    return ret_data_frame


def get_basic_block(module, offset):
    assert isinstance(module, elffile_mod.ELFFile)
   # assert isinstance(offset, int)
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
    #assert isinstance(offset_list, collections.Iterable), "Expected an iterable object, got %s" % type(offset_list)
    ret = []
    for offset in offset_list:
        ret.append(get_basic_block(module, offset))
    return ret

if __name__ == "__main__":
    # e = elffile_mod.ELFFile("/home/paszoste/cp/tests/files/test_elf")
    # bb = get_basic_block(e, 0x81f)
    # for inst in bb:
    #     print inst.get_mnemonic_intel(), inst.get_length(), inst.get_operand_width(), inst.get_number_of_operands(), bytes_to_string(inst.get_bytes())
    from pandas import DataFrame
    bb_df = DataFrame.from_csv("../../csv/libCore.so.stat.csv")
    bbs = list(bb_df.index)
    disassembly = get_disassembly_for_basic_blocks({"../../dsos/libCore.so":bbs})
    print(disassembly)
    disassembly.to_csv('libCore.so.disassembly.csv')

