#!/usr/bin/env python

import pandas, sys, re
from symcollector import symcollector

def getSymbols(name):
	symbols = symcollector.collect(name)
	symbols = symbols[["addr","size","name"]]
	filtered = symbols[ (symbols.addr > 0) & (symbols.size > 0) ]
	filtered["end"] = filtered["addr"] + filtered["size"]
	final = filtered[["addr","end","name"]]
	final.columns = ["start", "end", "name"]
	return final

def getFunctions(name):
	symbols = symcollector.collect(name)
	symbols = symbols[symbols.type == "FUNC"]
	symbols = symbols[["addr","size","name"]]
	filtered = symbols[ (symbols.addr > 0) & (symbols.size > 0) ]
	filtered["end"] = filtered["addr"] + filtered["size"]
	final = filtered[["addr","end","name"]]
	final.columns = ["start", "end", "name"]
	return final

def getClassName(row):
	name = row["name"]

	# Get rid of parantheses
	if "(" in name:
		name = name[:name.rindex("(")]

	# Get rid of function name
	if "::" in name:
		name = name[:name.rindex("::")]
		return name
	
	return None


def findClasses(df):
	chopped = df.apply(getClassName, axis=1)
	chopped = pandas.DataFrame(chopped, columns=["name"])
	chopped = chopped.drop_duplicates(cols="name")
	chopped = chopped.dropna(axis=0)
	return chopped

def filterByName(df, name):
	return df[ df.name.str.startswith(name) ]

def aggregateByName(df, name):
	filtered = filterByName(df, name)


def main():
	path = sys.argv[1]

	funcs = getFunctions(path)
	# filterByName(syms, "feather::Ns_ConstrXeqYandZ")
	classes = findClasses(funcs)
	print(classes)

	for className in classes.iterrows():
		name = className[1].values[0]
		print("Class: {0}".format(name))
		print(filterByName(funcs, name))
		print("\n")

if __name__ == '__main__':
	main()