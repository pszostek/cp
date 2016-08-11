import cp.elf as elf
import cp.elf.disass as disass
import cp.xed.xed as xed
import cp.elf.addr2line as addr2line

if __name__ == "__main__":
    # this is a `good' binary with .symtab and DWARF
    binary = elf.ELFFile("./real_data/fullcms")

    # get all the BBs from disassembly
    bbs = xed.get_static_bbs(binary)
    # XXX: was:
    # bytes = open(binary._path).read()
    # xed.newer_detect_static_basic_blocks(bytes)
    print("Test BB info: %s" % str(bbs[0]))

    # we need some offsets - let's take starting addresses of some BBs
    start_addrs = [bb.start for bb in bbs]

    # addr2line.init() has to be called for every binary we want to use it for
    # Since this method has a non-negligible cost, it makes sense to do it not
    # more than once per file
    addr2line.init(binary)
    # XXX: was:
    # addr2line.initialize_line_numbers(binary._path)

    # translate offsets to line info
    line_numbers = [addr2line.find_line_number(start_addr) for start_addr in start_addrs]
    print("Test line info: %s" % line_numbers[0])

    # get demangled symbol name for an offset based on .symtab
    magic_offset = 0x524b50
    symbol = binary.get_symbol_by_offset(magic_offset)
    print("Test symbol: %s" % str(symbol))

    # get info for the the first basic blocks
    inst_lists = binary.get_inst_lists([(bb.start, bb.end) for bb in bbs][:10])
    # XXX: was:
    # inst_lists = \
    #       binary.get_inst_lists_for_basic_blocks(
    #           {binary._path:[(bb.start, bb.end) for bb in bbs if bb.start >= 0x440][:10]})
    print("Test inst list: %s" % str(inst_lists))

