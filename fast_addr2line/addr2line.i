%module addr2line

%include "typemaps.i"


%include "cstring.i"
%include "stdint.i"
%include "std_pair.i"
%include "std_vector.i"
%include "std_string.i"

%typemap(in, numinputs=0) std::string& file(std::string temp) "$1 = &temp;"
%typemap(argout) std::string&
{
    PyObject* obj = PyUnicode_FromStringAndSize((*$1).c_str(),(*$1).length());
    $result=SWIG_Python_AppendOutput($result, obj);
}

%typemap(in,numinputs=0) xed_uint32_t& line (xed_uint32_t temp) "$1 = &temp;"

%typemap(argout) xed_uint32_t& line {
  %append_output(PyInt_FromLong(*$1));
}

%{
    #include "fast_addr2line.h"
    extern int correct_find_line_number(uint64_t addr, std::string& file,  xed_uint32_t& line);
    extern void initialize_line_numbers(char* input_file_name);
%}
%include "fast_addr2line.h"


%template(IntPair) std::pair<int, int>;
%template(PairVector) std::vector<std::pair<int, int> >;
%template(IntVector) std::vector<int>;

