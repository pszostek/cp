%module xed

%include "carrays.i"
%array_class(uint8_t, bytearray)
%include "exception.i"
%include "stdint.i"
%include "typemaps.i"
%include "cstring.i"

// for functions like void dump(char* buf, int buflen)
// this allows to omit the first argument and to return
// a Python-string instead of a null


%typemap(in) (char* data, unsigned int length) {
  if (!PyString_Check($input)) {
    PyErr_SetString(PyExc_ValueError, "Expecting a string");
    return NULL;
  }
  $1 = PyString_AsString($input);
  $2 = PyString_Size($input);
}
%{
    #include <assert.h>
    #include "xed_disass.h"
    extern inst_list_t* disassemble_x86(char* data, unsigned int length);
    extern inst_list_t* disassemble_x64(char* data, unsigned int length);
    extern inst_list_t* _disassemble(xed_state_t xed_state, char* data, unsigned int length);

    extern inst_list_t* disassemble_x86_until_bb_end(char* data, unsigned int length);
    extern inst_list_t* disassemble_x64_until_bb_end(char* data, unsigned int length);
    extern inst_list_t* _disassemble_until_bb_end(xed_state_t xed_state, char* data, unsigned int length);

    extern void print_operand_width(const xed_decoded_inst_t* p);
    static int iter_error = 0;
%}

%inline %{
    struct inst_list_iter {
        inst_list_t* list;
        size_t pos;
    };
%}

%exception inst_list_iter::next {
    assert(!iter_error);
    $action
    if (iter_error) {
        iter_error = 0;
        PyErr_SetString(PyExc_StopIteration, "End of iteration");
        return NULL;
    }
}

%extend inst_list_iter {
    struct inst_list_iter* __iter__() {
        return $self;
    }

    xed_decoded_inst_t* next() {
        if($self->pos < $self->list->size) {
            return &($self->list->inst_array[$self->pos++]);
        }
        iter_error = 1;
        return NULL;
    }

    xed_decoded_inst_t* __next__() {
        inst_list_iter_next($self);
    }
}

%include "include/xed-types.h"
%include "include/xed-common-defs.h"
%include "include/xed-common-hdrs.h"
%include "include/xed-portability.h"
%include "include/xed-interface.h"
%include "include/xed-decoded-inst.h"
%include "include/xed-inst.h"
%include "include/xed-category-enum.h"
%include "include/xed-iclass-enum.h"
%include "include/xed-operand-values-interface.h"
%include "xed_disass.h"



%array_class(char, bytesArray)
%extend xed_decoded_inst_t {

    //  This macro is used to return strings that are allocated within the program 
    // and returned in a parameter of type char **. The argument of type char** will be
    // null-terminated.

    %cstring_output_allocate(char** buffer, free(*$1));

    // for python::xed.xed_decoded_inst_dump()
    %cstring_output_maxsize(char* buf, int buflen);

    void get_mnemonic(char** buffer) {
        *buffer = (char*) malloc(512);
        xed_decoded_inst_dump($self, *buffer, 512);
    }

    void get_mnemonic_intel(char** buffer) {
        *buffer = (char*) malloc(64);
        xed_decoded_inst_dump_intel_format($self, *buffer, 64, 0);
    }

    void __str__(char** buffer) {
        xed_decoded_inst_s_get_mnemonic_intel($self, buffer);
    }

    void get_mnemonic_att(char** buffer) {
        *buffer = (char*) malloc(64);
        xed_decoded_inst_dump_att_format($self, *buffer, 64, 0);
    }

    unsigned int get_number_of_operands() {
        return xed_decoded_inst_noperands($self);
    }

    const char* get_iclass() {
        char buffer[32];
        xed_iclass_enum_t iclass = xed_decoded_inst_get_iclass((const xed_decoded_inst_t*)$self);
        return xed_iclass_enum_t2str(iclass);
    }

    const xed_iclass_enum_t get_iclass_code() {
        return xed_decoded_inst_get_iclass((const xed_decoded_inst_t*)$self);
    }

    const char* get_category() {
        char buffer[32];
        xed_category_enum_t category = xed_decoded_inst_get_category((const xed_decoded_inst_t*)$self);
        return xed_category_enum_t2str(category);
    }

    const xed_category_enum_t get_category_code() {
        return xed_decoded_inst_get_category((const xed_decoded_inst_t*)$self);
    }

    const unsigned int get_length() {
        return xed_decoded_inst_get_length($self);
    }

    %cstring_output_allocate_size(char** bytes, unsigned int* bytes_len, free(*$1));
    void get_bytes(char** bytes, unsigned int* bytes_len) {
        unsigned int length = xed_decoded_inst_get_length($self);
        // printf("%d length\n", length);
        *bytes  = (char*) malloc(length);
         // printf("malloced\n");
        for (int idx=0; idx < length; ++idx) {
            (*bytes)[idx] = (char)xed_decoded_inst_get_byte($self, idx);
            //xed_decoded_inst_get_byte($self, idx);
            //(*bytes)[idx] = '1';
            // printf("byte\n");
        }
        *bytes_len = length;
        // printf("end\n");
    }
}

%extend inst_list_t {

    xed_decoded_inst_t* __getitem__(int i) {
        if(abs(i) >= $self->size) {
            iter_error = 1;
            return NULL;
        }
        if(i < 0) {
            return &($self->inst_array[$self->size+i]);
        }
        return &($self->inst_array[i]);
    }
    inst_list_t* __getitem__(PyObject* slice) {
        Py_ssize_t start, stop, step;
        size_t idx;
        PySlice_GetIndices((PySliceObject*)slice, $self->size, &start, &stop, &step);
        size_t ret_size = stop-start;
        inst_list_t* ret = (inst_list_t*)malloc(sizeof(inst_list_t));
        inst_list_init_size(ret, ret_size);
        for(idx=start; idx<stop; idx += step) {
            inst_list_append(ret, inst_list_get($self, idx));
        }
        return ret;
    }
    struct inst_list_iter* __iter__() {
        struct inst_list_iter* ret = (struct inst_list_iter*)malloc(sizeof(struct inst_list_iter)); ret->list = $self;
        ret->pos = 0;
        return ret;
    }

    size_t __len__() {
        return $self->size;
    }
}

%exception inst_list_t::__getitem__ {
    assert(!myErr);
    $action;
    if (iter_error) {
        iter_error = 0;
        SWIG_exception(SWIG_IndexError, "Index out of bounds");
    }
}
// XED_INLINE -> inline
// xed_strcat -> //xed_strcat
// xed_uint32_t -> uint32_t etc.
// comment out xed_operand_values_is_prefetch
// comment out xed_operand_values_has_disp
// xed_bool_t