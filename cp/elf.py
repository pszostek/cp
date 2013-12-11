#!/usr/bin/env python
#-*- encoding: utf8 -*-

from __future__ import print_function
from collections import namedtuple
from demangle import demangle
from elftools.common.py3compat import bytes2str
from elftools.elf.elffile import ELFFile as ELFFile_

Func = namedtuple("Func", ["name", "mangled_name", "offset", "size"])


class ELFFileError(Exception):
    def __init__(self, what):
        Exception.__init__(self, what)

class ELFFile(ELFFile_):
    def __init__(self, filepath):
        self._fd = open(filepath, 'rb')
        ELFFile_.__init__(self, self._fd)

    def __del__(self):
        self._fd.close()

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
        symtab = self._get_symbol_table()
        return self._iter_func(symtab.iter_symbols())

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

    def get_text_from_offset(self, offset):
        pass

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

    def _iter_func(self, symbols_iter):
        for sym in symbols_iter:
            if sym.entry['st_info']['type'] == 'STT_FUNC':
                demangled_name = demangle.cplus_demangle(sym.name, 1)
                if demangled_name is not None:
                    name = demangled_name
                else:
                    name = sym.name
                yield Func(name=name,
                           mangled_name=sym.name,
                           offset=sym.entry['st_value'],
                           size=sym.entry['st_size'])
        raise StopIteration()

    def _offset_inside_section(self, offset, section):
        sh = section.header
        return (offset >= sh['sh_offset']) and (offset < sh['sh_offset']+sh['sh_size'])

  #  def _offset_inside_segment(self, offset, segment):
  #      sh = segment.header
  #      return (offset >= sh['p_paddr']) and (offset < sh['p_paddr']+sh['p_filesz'])

if __name__ == "__main__":
    elf = ELFFile("/home/paszoste/cp/cp/xed-ex1")
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