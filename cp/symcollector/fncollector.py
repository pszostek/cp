
import pandas, symcollector

def filterSymbols(df):
    df = df[["addr","size","name"]]
    filtered = df[ (df.addr > 0) & (df.size > 0) ]
    filtered["end"] = filtered["addr"] + filtered["size"]
    final = filtered[["addr","end","name"]]
    final.columns = ["start", "end", "name"]
    return final

# Receives a string with the filename of the dso
def getSymbols(dso):
    symbols = symcollector.collect(dso)
    return filterSymbols(symbols)

# Receives a string with the filename of the dso
def getFunctions(dso):
    symbols = symcollector.collect(dso)
    symbols = symbols[symbols.type == "FUNC"] 
    return filterSymbols(symbols)

def extractClassname(row):
    name = row["name"]

    # Get rid of parantheses
    if "(" in name:
        name = name[:name.rindex("(")]

    # Get rid of function name
    if "::" in name:
        index = len(name)-1
        depth = 0
        while not (name[index] == ":" and depth == 0):
            chopped = name[:index]

            if chopped.endswith("operator>>") or chopped.endswith("operator<<"):
                index -= 10
                continue

            if chopped.endswith("operator>") or chopped.endswith("operator<"):
                index -= 9
                continue

            if name[index] == ">":
                depth += 1
            if name[index] == "<":
                depth -= 1
            index -= 1
        index -= 1
        return name[:index]
    return None

# Receives the output from getFunctions and returns
# just the names of the classes (or toplevel namespaces
# in which there are functions not belonging to a class)    
def getClassnames(df):
    classnames = df.apply(extractClassname, axis=1)
    classnames = pandas.DataFrame(classnames, columns=["name"])
    classnames = classnames.drop_duplicates(cols="name")
    classnames = classnames.dropna(axis=0)
    return classnames


