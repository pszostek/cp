#!/usr/bin/env python

import subprocess, os.path, pandas, re
from collections import defaultdict

# import demangle
# from elftools.elf.elffile import ELFFile

class CollectionError(Exception):
	def __init__(self, text, stdout, stderr):
		super(CollectionError, self).__init__(text)
		self.stdout = stdout
		self.stderr = stderr

# Returns a list with [address, line_number] for all
# symbols for which it is available
def getLineNumbers(location):
	p = subprocess.Popen(["nm", "-l", location], stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	stdout, stderr = p.communicate()

	if p.returncode != 0:
		raise CollectionError("An error occured while running nm", stdout, stderr)

	stdout = stdout.split("\n")

	linenumbers = []

	for line in stdout:
		line = line.split()
		if len(line) == 4:
			linenumbers.append( (int(line[0], 16), line[3]) )

	return linenumbers

# def collectInPython(location):
# 	e = ELFFile(open(location, 'rb'))
# 	symtab = e.get_section_by_name('.symtab')
# 	symbols = []
	
# 	for idx, symbol in enumerate(symtab.iter_symbols()):
# 		se = symbol.entry
# 		symbols.append((idx,
# 					se['st_value'],
# 					demangle.cplus_demangle( symbol.name, 1 ),
# 					se['st_size'],
# 					se['st_info']['type'],
# 					se['st_info']['bind'],
# 					se['st_other']['visibility'],
# 					None))

# 	return symbols


def collect(location):

	if not os.path.isfile(location):
		raise IOError("{} is not a file".format(location))


	p = subprocess.Popen(["readelf -Ws {} | c++filt".format(location)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True )
	stdout, stderr = p.communicate()

	if p.returncode != 0:
		raise CollectionError("An error occured while running readelf", stdout, stderr)

	stdout = stdout.strip()

	# Is there a .symtab?
	symtab = stdout.find("Symbol table '.symtab' contains")	
	if symtab != -1:
		# Yes, there is. No need to parse .dynsym since it is only a subset of .symtab
		# Skip until .symtab
		stdout = stdout[symtab:]

	stdout = stdout.split("\n")

	symbols = []
	addr_lookup = defaultdict(list)

	# Parse output and build the list of symbols
	for line in stdout[2:]:
		line = line.split(None, 7)

		sym_id = int(line[0][:-1])
		sym_addr = int(line[1], 16 )
		
		if len(line) > 7:
			name = line[7]
		else:
			name = None

		size = int(line[2], 0)
		if size == 0:
			size = None

		sym_type = line[3]
		bind = line[4]
		vis = line[5]
		ndx = line[6]
		if ndx.isdigit():
			ndx = int(ndx)

		symbols.append( [sym_id, sym_addr, name, size, sym_type, bind, vis, ndx, None] )
		addr_lookup[sym_addr].append( len(symbols) - 1 )


	# Get linenumbers from nm and match them against what we already have
	# if symtab != -1:
	# 	linenumbers = getLineNumbers(location)

	# 	for (address, linenumber) in linenumbers:
	# 		for i in addr_lookup[address]:
	# 			symbols[i][8] = linenumber

	# return symbols

	# for i in symbols:
	# 	print(i)


	return pandas.DataFrame(symbols, columns=["id", "addr", "name", "size", "type", "bind", "vis", "ndx", "line" ])

if __name__ == '__main__':
	# Example usage
	df = collect("../../dsos/libCore.so")
	df.to_csv("libCore.so.symbols.csv")

