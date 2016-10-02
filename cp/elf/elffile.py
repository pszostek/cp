#!/usr/bin/env python
#-*- encoding: utf8 -*-

from __future__ import print_function
from collections import namedtuple
from pyelftools.elftools.elf.elffile import ELFFile as ELFFile_
from pyelftools.elftools.elf.sections import Section, Symbol
from pyelftools.elftools.common.py3compat import bytes2str

Func = namedtuple("Func", ["name", "mangled_name", "poff", "size"])

if __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

class ELFFileError(Exception):
    def __init__(self, what):
        Exception.__init__(self, what)


class ELFFile(ELFFile_):
    def __init__(self, filepath):
        self._path = filepath
        self._fd = open(filepath, 'rb')
        self.__symbol_interval_tree = None
        ELFFile_.__init__(self, self._fd)

    # a method allowing buidling the Symbol Interval Tree lazily
    def get_symbol_interval_tree(self):
        if self.__symbol_interval_tree is None:
            self.__symbol_interval_tree = self._build_symbol_tree()
        return self.__symbol_interval_tree

    def set_symbol_interval_tree(self, sth):
        self.__symbol_interval_tree = sth

    _symbol_interval_tree = property(get_symbol_interval_tree, set_symbol_interval_tree)

    def __del__(self):
        self._fd.close()

    def get_offset_for_virtual_address(self, vaddr):
        correct_segment = None
        for segment in self.iter_segments():
            if (segment['p_vaddr'] >= vaddr and
                vaddr < segment['p_vaddr'] + segment['p_filesz']):
                correct_segment = segment
                break

        if correct_segment is not None:
            correct_section = None
            for section in self.iter_sections():
                if correct_segment.section_in_segment(section):
                    correct_section = section
                    break
            if correct_section is not None:
                offset_in_segment = vaddr - correct_segment['p_vaddr']
                return correct_section['sh_offset'] + offset_in_segment
            else:
                return None
        else:
            return None

    def get_virtual_address_for_offset(self, offset):
        section = self.get_section_by_offset(offset)
        offset_from_section_start = offset - section['sh_offset']
        section_vaddr = self.get_section_virtual_address(section)
        return section_vaddr + offset_from_section_start

    def get_section_by_offset(self, offset):
        for section in self.iter_sections():
            if offset >= section['sh_offset'] and offset < section['sh_offset'] + section['sh_size']:
                return section
        return None

    def get_segment_by_virtual_address(self, vaddr):
        for segment in self.iter_segments():
            if segment['p_vaddr'] >= vaddr and vaddr < segment['p_vaddr'] + segment['p_filesz']:
                return segment
        return None

    def get_section_by_virtual_address(self, vaddr):
        segment = self.get_segment_by_virtual_address(vaddr)
        for section in self.iter_section():
            if segment.section_in_segment(section):
                return section
        return None

    def get_section_virtual_address(self, section):
        assert isinstance(section, Section)
        matching_segments = []
        for segment in self.iter_segments():
            if segment.section_in_segment(section):
                matching_segments.append(segment)
        return max(matching_segments, key=lambda s: s['p_filesz'])

    def get_symbol_by_name(self, name):
        for symbol in self.iter_symbols():
            if symbol.name == name:
                return symbol
        # if we reached this point, then there is no such symbol in the file
        raise ELFFileError("The file has no %s symbol" % name)

    def get_function_by_mangled_name(self, mangled_name):
        for func in self.iter_functions():
            if func.mangled_name == mangled_name:
                return func
        raise ELFFileError("There is no function with mangled name %s" % mangled_name)

    def get_function_by_name(self, name):
        for func in self.iter_functions():
            if func.name == name:
                return func
        raise ELFFileError("There is no %s function" % name)

    def iter_symbols(self):
        sym_name = b".symtab"
        symtab = self.get_section_by_name(sym_name)
        if symtab is None:
            raise ELFFileError('The file has no %s section' % bytes2str(sym_name))
        return symtab.iter_symbols()

    def iter_functions(self):
        #symtab = self._get_symbol_table()
        #return self._iter_func(symtab.iter_symbols())
        return self._iter_func() # it will get symtab or dynsym automatically

    def get_symbol_text(self, name):
        if name not in self.get_symbol_names():
            raise ELFFileError('The file has no % symbol' % name)
        text_section_offset = self._get_text_offset()
        symbol = self.get_symbol_by_name(name)

        # rewind the file to be at the symbol position
        symbol_size = symbol.entry["st_size"]
        symbol_offset = symbol.entry["st_value"]

        # remember the current position in order to go back afterwards
        cur = self._fd.tell()
        self._fd.seek(symbol_offset-text_section_offset)
        text = self._fd.read(symbol_size)
        self._fd.seek(cur)
        return text

    def get_function_names(self):
        return [func.name for func in self._iter_func()]

    def old_get_function_names(self):
    # print('Processing file:', filename)
        sym_name = b'.symtab'
        symtab = self.get_section_by_name(sym_name)
        if symtab is None:
            raise ELFFileError('The file has no %s section' % bytes2str(sym_name))
        return [func.name for func in self._iter_func(symtab.iter_symbols())]

    def get_symbol_names(self):
        return [symbol.name for symbol in self.iter_symbols()]

    def get_section_names(self):
        return [symbol.name for symbol in self.iter_sections()]

    def get_text(self):
        text = self.get_section_by_name('.text')

        if text is None:
            raise ELFFileError("ELF file has no .text section")
        return text.data()

    def get_section_by_offset(self, offset):
        for section in  self.iter_sections():
            if self._offset_inside_section(offset, section):
                return section
        raise ELFFileError("There is no section that contains given offset: %d" % offset)

    def get_inst_lists(self, addrs_list):
        """ A proxy method for a proper disassembly function"""
        import disass  # this is imported only when we need to disassemble
        return disass.get_inst_lists(self, addrs_list)

    def get_symbol_by_poff(self, offset):
        """
        Figures out name of the symbol for the given offset.

        poff -- a number expressing the physical offset inside the ELF file

        Returns None or a string. None is returned when there is no corresponding symbol
        (e.g. the binary is stripped or the offset is malformed)
        Otherwise returns demangled symbol name
        """
        symbol = self._symbol_interval_tree.search(offset) # returns a set
        if not symbol: #an empty set
            return None
        else:
            #assert len(symbol) == 1
            return list(symbol)[0].data # sets are not indexed, must be converted to a list

    def get_text_by_offset(self, offset):
        pass

    def has_symtab(self):
        symtab = self._get_symbol_table()
        return symtab is not None

    def has_dynsym(self):
        dynsym = self._get_dynsym_table()
        return dynsym is not None

### private functions ###

    def _get_text_offset(self):
        text_section = self.get_section_by_name('.text')
        for segment in self.iter_segments():
            if segment.section_in_segment(text_section):
                return segment['p_paddr']
        raise ELFFileError("Section .text is not present in the ELF file")

    def _get_symbol_table(self):
        sym_name = b'.symtab'
        symtab = self.get_section_by_name(sym_name)
        return symtab

    def _get_dynsym_table(self):
        sym_name = b'.dynsym'
        dynsym = self.get_section_by_name(sym_name)
        return dynsym

    def _iter_func(self, symbols_iter=None):
        from ..demangle import demangle
        if symbols_iter is None:
            if self.has_symtab():
                symtab = self._get_symbol_table()
                symbols_iter = symtab.iter_symbols()
            elif self.has_dynsym():
                dynsym = self._get_dynsym_table()
                symbols_iter = dynsym.iter_symbols()
            else:
                raise StopIteration()

        symbols_list = list(symbols_iter)
        sym_start_vaddrs = [sym['st_value'] for sym in symbols_list]
        guessed_symbol_sizes = self._compute_symbol_sizes(sym_start_vaddrs)
        for sym in symbols_list:
            if sym.entry['st_info']['type'] == 'STT_FUNC' and sym['st_shndx'] is not 'SHN_UNDEF':
                demangled_name = demangle.cplus_demangle(sym.name, 1)
                if demangled_name is not None:
                    name = demangled_name
                else:
                    name = sym.name
                adj = self._symbol_to_poff_adj(sym)
                sym_size = 0
                sym_poff = sym.entry['st_value'] + adj
                if sym.entry['st_size'] is not 0:
                    sym_size = sym.entry['st_size']
                else:
                    try:
                        sym_size = guessed_symbol_sizes[sym.entry['st_value']]
                    except KeyError:  # nope, we don't have this value
                        pass  # oh well, the symbol will be zero-sized
                yield Func(name=name,
                           mangled_name=sym.name,
                           poff=sym_poff,
                           size=sym_size)
        raise StopIteration()

    def _offset_inside_section(self, offset, section):
        sh = section.header
        return (offset >= sh['sh_offset']) and (offset < sh['sh_offset']+sh['sh_size'])

    def _build_symbol_tree(self):
        from intervaltree import IntervalTree, Interval
        # Interval expects addresses (first, one_after)
        #for idx, func in enumerate(self._iter_func()):
        #        print(idx, func.name, hex(func.poff), hex(func.poff+func.size))
        intervals = [Interval(func.poff, func.poff+func.size, func.name) for func in self._iter_func() if func.size != 0]
        return IntervalTree(intervals)

    def _compute_symbol_boundaries(self, symbol_poffs):
        symbol_poffs = sorted(symbol_poffs)
        sym_poff_boundaries = zip(symbol_poffs[:-1], [a-1 for a in symbol_poffs][1:])
        # add the last boundary
        sym_poff_boundaries.append((symbol_poffs[-1], symbol_poffs[-1] + 0x1000)) # no idea where the last symbol ends
        return sym_poff_boundaries

    def _compute_symbol_sizes(self, symbol_poffs):
        # input: a list of symbol starting addresses
        # returns a dictionary (starting address: size)
        sym_poff_boundaries = self._compute_symbol_boundaries(symbol_poffs)
        sym_poff_to_size_list = [(start, end-start+1) for (start, end) in sym_poff_boundaries]
        return dict(sym_poff_to_size_list)

    def _symbol_to_poff_adj(self, symbol):
        """ symbol is an elf.Symbol """
        assert(isinstance(symbol, Symbol))
        sym_section = self.get_section(symbol['st_shndx'])
        adj = sym_section['sh_offset'] - sym_section['sh_addr']
        return adj


class Kernel(ELFFile):
    def __init__(self, filepath, sysmap_filepath, lazy=False):
        ELFFile.__init__(self, filepath)
        if self.lazy: # if lazy is set, the poff_to_sym table will be built later, on iteration
            self._poff_to_sym = None
        else:
            self._poff_to_sym = self._build_poff_to_sym(sysmap_filepath)

    def _build_poff_to_sym(self, sysmap_filepath):
        ret = {}
        with open(sysmap_filepath, 'r') as sysmap_fd:
            for line in sysmap_fd.readlines():
                (sym_vaddr, sym_type, sym_name) = line.split()
                if sym_type not in set(['t', 'T']):
                    continue
                sym_vaddr = int(sym_vaddr, 16)
                sym_poff = sym_vaddr + self._get_vaddr_to_poff_adj()
                if sym_poff in ret: # oops, overlaping symbols..
                    existing_sym = ret[sym_poff]
                    concat_name = "%s:%s" % (existing_sym, sym_name)
                    ret[sym_poff] = concat_name
                else: # we see this address for the first time
                    ret[sym_poff] = sym_name
        return ret

    def _build_symbol_tree(self):
        from intervaltree import IntervalTree, Interval
        intervals = [Interval(func.poff, func.poff+func.size, func.name) for func in self._iter_func() if func.size != 0]
        return IntervalTree(intervals)

    def _get_vaddr_to_poff_adj(self):
        from pyelftools.elftools.elf.constants import P_FLAGS
        load_vaddr = None
        for segment in self.iter_segments():
            if segment['p_type'] == "PT_LOAD" and segment['p_flags'] == (P_FLAGS.PF_X | P_FLAGS.PF_R):
                load_vaddr = segment['p_vaddr'];
                break
        if load_vaddr is None:
            raise RuntimeError("Can't find a loadable program segment with r-x flags")
        text = self.get_section_by_name(".text")
        return -load_vaddr + text['sh_offset']

    def _iter_func(self, symbols_iter=None):
        if self._poff_to_sym is None:
            self._poff_to_sym = self._build_poff_to_sym(sysmap_filepath)
        sym_start_poff = sorted(self._poff_to_sym.keys())
        sym_poff_boundaries = self._compute_symbol_boundaries(sym_start_poff)

        for (sym_start_poff, sym_end_poff) in sym_poff_boundaries:
                yield Func(name=self._poff_to_sym[sym_start_poff],
                           mangled_name=self._poff_to_sym[sym_start_poff],
                           poff=sym_start_poff,
                           size=sym_end_poff-sym_start_poff+1)
        raise StopIteration()


if __name__ == "__main__":
    elf = ELFFile("/afs/cern.ch/user/p/paszoste/cp/simple-binary/a.out")
    print(elf.get_symbol_by_offset(int('731', 16)))
    print(elf.get_symbol_by_offset(int('982', 16)))
    print(elf.get_symbol_by_offset(int('9cd', 16)))
    print(elf.get_symbol_by_offset(int('9f5', 16)))
    print(elf.get_symbol_by_offset(int('a42', 16)))
    # for symbol in elf.iter_symbols():
    #     print(symbol.name, symbol.entry["st_size"], symbol.entry["st_value"])
    textsec = elf.get_section_by_name('.text')
    # print("SECTION")
    # for sec in elf.iter_sections():
    #     print(sec.header)
    #     if sec['sh_type'] == 'SHT_STRTAB':
    #         print(sec.get_string(49))
    # print("SEGMENT")
    # for seg in elf.iter_segments():
    #     print(seg.section_in_segment(textsec), seg.header)
    # print(elf._get_text_offset())
    text = elf.get_symbol_text("main")
    main_file = open("main_text", "wb")
    for segment in elf.iter_sections():
        print(segment.header)
    main_file.write(text)
    print(len(text))
    import xed
    inst_list = xed.disassemble(1, text, len(text))
    print(len(inst_list))
    for inst in inst_list:
        print(inst)
        print(xed.xed_decoded_inst_dump_intel_format(inst, 1024, 0))
