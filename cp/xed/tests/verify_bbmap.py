#!/usr/bin/env python2.7

# AN

# This script uses the following heuristic method to check if the chopper screwed up.
#    objdump is used to dump all addresses in the .text section of a binary module.
#    we then verify if all bb offset addresses produced by the chopper fit in a subset 
#    the addresses presented by objdump (as they should) 

import pandas as p, os, sys

def make_dso_bbmap(fname):
    csvfname = "/tmp/" + os.path.basename(fname)+".bbmap.TMPcsv"
    if not os.path.exists(csvfname):
        retval = os.system("/data/andrzejn/ne/chopper2 %s %s" % (fname, csvfname));
        if retval != 0:
            print "\tmaking a bbmap for %s failed" % fname
            raise IOError

    bbmap = p.read_csv(csvfname, converters={
          0: lambda x: int(x, 16),
          1: lambda y: int(y, 16),
          2: lambda z: int(z)} )

    return bbmap

fname = sys.argv[1]
# run objdump on the same file
cmd = "objdump -D -j .text %s  | egrep '[0-9a-f]+:' | cut -f1 | tr -d : > /tmp/objdump.TMPcsv" % fname
df_objdump = p.read_csv("/tmp/objdump.TMPcsv", names=["bb_objdump"], converters={0: lambda x: int(x, 16)})
df_chopper = make_dso_bbmap(fname)

# compare to what objdump is showing
result = df_objdump.merge(df_chopper, how="outer", left_on="bb_objdump", right_on="bb", left_index=False, right_index=False)
diff = result[p.isnull(result.bb_objdump)]
diff.loc[:, "bb"] = diff.loc[:, "bb"].apply(lambda x: hex(x).rstrip("L"))
diff.loc[:, "bb_end"] = diff.loc[:, "bb_end"].apply(lambda x: hex(x).rstrip("L"))
print "There are %d blocks that the chopper detected which are not valid instruction start addresses in objdump. Dump follows:" % len(diff)
print diff
print "%d blocks are inconsistent" % len(diff)
