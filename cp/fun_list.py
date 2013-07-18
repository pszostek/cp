#!/usr/bin/env python
#-*- encoding: utf8 -*-

from __future__ import print_function
from collections import namedtuple
import sys
from demangle import demangle
Func = namedtuple("Func", ["name", "elfname", "offset", "size", "instructions"])

from elftools.common.py3compat import bytes2str
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection


def get_symbols(filename):
    # print('Processing file:', filename)
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        sym_name = b'.symtab'
        symtab = elffile.get_section_by_name(sym_name)
        if symtab is None:
            print('  The file has no %s section' % bytes2str(sym_name))
            quit()

        # for sym in symtab.iter_symbols():
        #     print(sym.entry)
        for func in iter_func(symtab.iter_symbols()):
            print(func)


def get_text(filename, length=False):
    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        text = elffile.get_section_by_name('.text')
        if text is None:
            print('The file has no .text section')
            quit()
        if length is False:
            # print('  '.join(["%02X" % ord(byte) for byte in text.data()]))
            print(text.data())
        else:
            print(len(text.data()))


def iter_func(iter_symbols):
    for sym in iter_symbols:
        if sym.entry['st_info']['type'] == 'STT_FUNC':
            demangled_name = demangle.cplus_demangle(sym.name, 1)
            if demangled_name is not None:
                name = demangled_name
            else:
                name = sym.name
            yield Func(name=name,
                       elfname=sym.name,
                       offset=sym.entry['st_value'],
                       size=sym.entry['st_size'],
                       instructions=0)
    raise StopIteration()

if __name__ == '__main__':
    assert len(sys.argv) > 2
    if sys.argv[1] == "-s":
        for filename in sys.argv[2:]:
            get_symbols(filename)
    elif sys.argv[1] == "-t":
        for filename in sys.argv[2:]:
            get_text(filename)
    elif sys.argv[1] == "-l":
        get_text(sys.argv[2], length=True)
