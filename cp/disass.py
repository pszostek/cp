import xed
import elf

def bytes_to_string(bytes):
    return ' '.join(map(lambda x: '%02x' % ord(x), bytes))

def get_basic_block(module, offset):
    assert isinstance(module, elf.ELFFile)
    fd = module._fd

    section = module.get_section_by_offset(offset)
    section_offset = section.header['sh_offset']
    section_size = section.header['sh_size']
    section_end = section_size + section_offset
    to_be_read = section_end - offset

    fd.seek(offset)
    bytes = fd.read(to_be_read)
    return xed.disassemble_x64_until_bb_end(bytes)

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
        print inst.get_mnemonic_intel(), bytes_to_string(inst.get_bytes())
