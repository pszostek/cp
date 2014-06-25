#!/usr/bin/env python

import sys, pandas
import symcollector
import symcollector.fncollector

# Merge lists of tuples 
# so that
# l = [(1, 2), (2, 3), (5, 6)]
# returns [(1,3), (5, 6)]
def merge(l):
    comb = sorted(l, key = lambda x: x[0])

    merged = [comb[0]]
    for c, d in comb[1:]:
       a, b = merged[-1]
       if c <= b < d:
           merged[-1] = a, d
       elif b < c < d:
           merged.append((c, d))
       else:
            # else case included for clarity. Since 
            # we already sorted the tuples and the list
            # only remaining possibility is c<d<b
            # in which case we can silently pass
            pass
    return merged

# Calculate the intersection from two lists
# of ranges
# ie for [(1, 4)] and [(2, 3)] should return [(2, 3)]
def intersection(l1, l2):
    pass
# Receives a dataframe that contains data from
# dynamic analysis and returns a cumulative version
def makeCumulative(df):
    sortedDf = df.sort(columns="addr")
    columns = list(sortedDf.columns.values)
    cumulative = pandas.DataFrame()
    cumulative["addr"] = sortedDf["addr"]
    for col in columns:
        if col == "addr":
            continue
        cumulative[col] = sortedDf[col].cumsum()
    cumulative.reindex(index=["addr"])
    return cumulative
class Tag(object):
    def __init__(self, start, end, label):
        if start is not None and end is not None:
            self.ranges = [(start, end)]
        else:
            self.ranges = []
        self.label = label
        self.children = []
        self.childLookup = {}
        self.cumulativeDf = []
    # Recursively feed the tag tree with dynamic analysis data
    # Input should be a dataframe with the *cumulative* values
    # from samples, sorted by address 
    def feed(self, cumulativeDf, cumulativeLookup):
        self.cumulativeDf = cumulativeDf
        self.cumulativeLookup = cumulativeLookup
    def addChild(self, tag):
        self.children += [tag] 
        self.childLookup[tag.label] = tag
    def lookup(self, label):
        return self.childLookup[label]
    def finalize(self):
        childranges = []
        for child in self.children:
            if self.cumulativeDf:
                child.cumulativeDf = self.cumulativeDf
                child.cumulativeLookup = self.cumulativeLookup
            child.finalize()
            childranges += child.ranges
        self.ranges = merge(self.ranges + childranges)

    def show(self, prefix=""):
        print(prefix + self.label)
        for r in self.ranges:
            print(prefix + str(r))
        for child in self.children:
            child.show(prefix + "\t")

# Receives a dataframe with (start, end, function name)
# and converts into a two-level tag hierarchy:
# Function
# |
# --- Fn1
# |
# --- Fn2
#
def functionTag(df):
    functions = Tag(None, None, "Functions")
    for index, row in df.iterrows():
        fn = Tag(int(row["start"]), int(row["end"]), row["name"])
        functions.addChild(fn)
    functions.finalize()
    functions.show()
    dynamicData = pandas.read_csv("/home/gbitzes/profiler/cp/cp/fakedata_shapes.csv")
    print(dynamicData)
    cumulative = makeCumulative(dynamicData)
    print(cumulative)
    cumulativeList = []
    for row in cumulative.iterrows():
        cumulativeList.append( (row[1]["addr"], row[0]))
    
    print(cumulativeList)
    return functions

# Receives a dataframe with (start, end, function name)
# and a list of classnames, and converts into a three-level
# tag hierachy:
# Class
# |
# -- Class1
# |  |
# |  --- Class1::Function1
# |
# -- Class2
#    |
#    --- Class2::Function3
def classTag(df):
    classnames = symcollector.fncollector.getClassnames(df)
    functions = functionTag(df)
    rootTag = Tag(None, None, "Classes")

    for index, c in classnames.iterrows():
        rootTag.addChild(Tag(None, None, c["name"]))

    print(classnames)
    print(df)
    for index, row in df.iterrows():
        # SLOW N^2 ALGORITHM!!!! SHOULD BE IMPROVED
        classname = symcollector.fncollector.extractClassname(row)
        if classname is not None:
            clTag = rootTag.lookup(classname)
            fnTag = functions.lookup(row["name"])
            clTag.addChild(fnTag)
    rootTag.finalize()
    rootTag.show()
    return rootTag

def main():
    df = symcollector.fncollector.getFunctions(sys.argv[1]) 
    functions = functionTag(df)
    functions.show("")

if __name__ == "__main__":
    main()

