import xed
import elf

def get_basic_block(module, offset):
    assert isinstance(module, elf.ELFFile)
    fd = module._fd

    section = module.get_section_by_offset(offset)
    section_offset = section.header['sh_offset']
    section_size = section.header['sh_size']
    section_end = section_size + section_offset
    to_be_read = section_end - offset

    fd.seek(section_offset)
    bytes = fd.read(to_be_read)
    print "call"
    return xed.disassemble_until_bb_end(xed.MODE_X64, bytes, len(bytes))

def get_basic_blocks(module, offset_list):
    assert isinstance(offset_list, list)
    ret = []
    for offset in offset_list:
        ret.append(get_basic_block(offset))
    return ret

if __name__ == "__main__":
    e = elf.ELFFile("/home/paszoste/cp/cp/xed-ex1")
    print 'bb'
    bb = get_basic_block(e, 0x14fdc4)
    print 'iter'
    for inst in bb:
        print inst.get_mnemonic_intel()
