%module disass

%include "carrays.i"
%array_class(uint8_t, bytearray)
%include "exception.i"
%include "stdint.i"
%include "typemaps.i"
%include "cstring.i"
%cstring_output_maxsize(char* buf, int buflen);

%{
    #include <assert.h>
    #include "xed_disass.h"
    extern inst_list_t* disassemble(int mode, char* data, unsigned int length);
    extern void print_operand_width(const xed_decoded_inst_t* p);
    static int myErr = 0;
%}

%exception inst_list_t::__getitem__ {
    assert(!myErr);
    $action;
    if (myErr) {
        myErr = 0;
        SWIG_exception(SWIG_IndexError, "Index out of bounds");
    }
}

%include "include/xed-common-defs.h"
%include "include/xed-common-hdrs.h"
%include "include/xed-portability.h"
%include "include/xed-interface.h"
%include "include/xed-decoded-inst.h"
%include "include/xed-inst.h"
%include "include/xed-category-enum.h"
%include "xed_disass.h"

%extend inst_list_t {
    xed_decoded_inst_t* __getitem__(size_t i) {
        if(i >= $self->inst_count) {
            myErr = 1;
            return &($self->inst[0]);
        }
        return &($self->inst[i]);
    }
}

%extend inst_list_t {
    size_t __len__() {
        return $self->inst_count;
    }
}
//XED_INLINE -> inline
//xed_strcat -> //xed_strcat