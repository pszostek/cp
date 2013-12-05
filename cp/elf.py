#!/usr/bin/env python
#-*- encoding: utf8 -*-

from __future__ import print_function
from collections import namedtuple
import sys
import os
from demangle import demangle
from elftools.common.py3compat import bytes2str
from elftools.elf.elffile import ELFFile_
from elftools.elf.sections import SymbolTableSection

Func = namedtuple("Func", ["name", "mangled_name", "offset", "size"])

class ELFFileError(Exception):
    def __init__(self, what):
        Exception.__init__(self, what)

class ELFFile(ELFFile_):
    def __init__(self, filepath):
        self._fd = open(filepath, os.O_RDONLY)
        ELFFile.__init__(self._fd)

    def __del__(self):
        self._fd.close()

    def get_symbol_text(self, symbolname):
        assert symbolname in self.get_symbol_names()
         

    def get_symbol_by_name(self):
        pass

    def get_symbol_names(self):
    # print('Processing file:', filename)
        sym_name = b'.symtab'
        symtab = self.get_section_by_name(sym_name)
        if symtab is None:
            raise ELFFileError('The file has no %s section' % bytes2str(sym_name))
        return [func.name for func in self._iter_func(symtab.iter_symbols())]

    def get_text(self):
        text = self.get_section_by_name('.text')

        if text is None:
            raise ELFFileError("ELF file has no .text section")
        return text.data()

    def _iter_func(self, symbols):
        for sym in symbols:
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
