%module addr2line

%include "typemaps.i"


%include "cstring.i"
%include "stdint.i"
%include "std_pair.i"
%include "std_vector.i"
%include "std_string.i"

// map input string reference to just string
%typemap(in, numinputs=0) std::string& file(std::string temp) "$1 = &temp;"
// map input-output reference to string to Python string
%typemap(argout) std::string&
{
    PyObject* obj = PyUnicode_FromStringAndSize((*$1).c_str(),(*$1).length());
    $result=SWIG_Python_AppendOutput($result, obj);
}

// map input referecnce to xed_uint32_t to the value behind
%typemap(in,numinputs=0) xed_uint32_t& line (xed_uint32_t temp) "$1 = &temp;"

// map input-output reference to xed_uint32_t to Python long
%typemap(argout) xed_uint32_t& line {
  %append_output(PyInt_FromLong(*$1));
}

%{
    #include "fast_addr2line.h"
%}
%include "fast_addr2line.h"

%pythoncode %{
def init(elffile):
    initialize_line_numbers(elffile._path)
    
import pandas
def collect():
    data = printall()
    data = data.strip().split("\n")
    ret = []
    # No dwarf?
    dwarf = True
    if data[0].startswith("#####"):
       dwarf = False 
    for line in data:
        # SKip data from stt symbols if we have dwarf
        if line.startswith("#####"):
            if dwarf:
                break
            else:
                continue     

        line = line.split("\t")
        tmp = line[2].split(":")
        path = tmp[0]
        num = tmp[1] 
        ret.append([line[0], line[1], path, num]) 
    return pandas.DataFrame(ret, columns=["start", "end", "path", "line"])
%}

