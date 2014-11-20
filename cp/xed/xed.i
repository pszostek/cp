%module xed

%include "carrays.i"
//%array_class(uint8_t, bytearray)
%include "exception.i"
%include "stdint.i"
%include "typemaps.i"
%include "cstring.i"
//http://www.swig.org/Doc1.3/Library.html#Library_stl_cpp_library
%include "std_list.i"




// for functions like void dump(char* buf, int buflen)
// this allows to omit the first argument and to return
// a Python-string instead of a null


// http://www.swig.org/Doc1.3/Library.html#Library_nn10
%apply (char* STRING, size_t LENGTH) { (char* elf_data, size_t fsize)};
%typemap(in) (char* data, unsigned int length) {
  if (!PyString_Check($input)) {
    PyErr_SetString(PyExc_ValueError, "Expecting a string");
    return NULL;
  }
  $1 = PyString_AsString($input);
  $2 = PyString_Size($input);
}

%typemap(in) (char* elf_data, unsigned int fsize) {
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
    #include "xed_bb_chop.h"
    extern inst_list_t* _disassemble_x86(char* data, unsigned int length, uint64_t base);
    extern inst_list_t* _disassemble_x64(char* data, unsigned int length, uint64_t base);
    extern inst_list_t* _disassemble(xed_state_t xed_state, char* data, unsigned int lengt, uint64_t base);

    extern inst_list_t* _disassemble_x86_until_bb_end(char* data, unsigned int length, uint64_t base);
    extern inst_list_t* _disassemble_x64_until_bb_end(char* data, unsigned int length, uint64_t base);
    extern inst_list_t* _disassemble_until_bb_end(xed_state_t xed_state, char* data, unsigned int length, uint64_t base);

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
            return $self->list->inst_array[$self->pos++];
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
%include "include/xed-operand-storage.h"
%include "include/xed-isa-set-enum.h"
%include "include/xed-attribute-enum.h"
%include "include/xed-operand-type-enum.h"
%include "include/xed-operand-width-enum.h"
%include "include/xed-operand-enum.h"
%include "include/xed-operand-action-enum.h"
%include "include/xed-operand-element-type-enum.h"

//%include "include/xed-operand-accessors.h"

%newobject _disassemble_x64;
%newobject _disassemble_x86;
%newobject _disassemble;

%newobject _disassemble_x64_until_bb_end;
%newobject _disassemble_x86_until_bb_end;
%newobject _disassemble_until_bb_ned;

%typemap(newfree) inst_list_t* {
    inst_list_delete($1);
}


%include "xed_disass.h"
%include "xed_bb_chop.h"

namespace std {
   %template(bbslist) list<bb_t>;
};

%array_class(char, bytesArray)
%extend xed_decoded_inst_t {

    //  This macro is used to return strings that are allocated within the program 
    // and returned in a parameter of type char **. The argument of type char** will be
    // null-terminated.

    %cstring_output_allocate(char** buffer, free(*$1));

    // for python::xed.xed_decoded_inst_dump()
    %cstring_output_maxsize(char* buf, int buflen);

    void dump_operand_info(char** buffer) {
        *buffer = (char*) malloc(512);
        xed_operand_values_dump(xed_decoded_inst_operands($self), *buffer, 512);
    }

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

    unsigned int get_operand_length(unsigned int idx) {
        return xed_decoded_inst_operand_length($self, idx);
    }

    const char* get_extension() {
        xed_extension_enum_t extension = xed_decoded_inst_get_extension((const xed_decoded_inst_t*)$self);
        return xed_extension_enum_t2str(extension);
    }

    const xed_extension_enum_t get_extension_code() {
        return xed_decoded_inst_get_extension((const xed_decoded_inst_t*)$self);
    }

    const char* get_isa_set() {
        xed_isa_set_enum_t isa_set = xed_decoded_inst_get_isa_set((const xed_decoded_inst_t*)$self);
        return xed_isa_set_enum_t2str(isa_set);
    }

    const xed_isa_set_enum_t get_isa_set_code() {
        return xed_decoded_inst_get_isa_set((const xed_decoded_inst_t*)$self);
    }

    const char* get_iclass() {
        xed_iclass_enum_t iclass = xed_decoded_inst_get_iclass((const xed_decoded_inst_t*)$self);
        return xed_iclass_enum_t2str(iclass);
    }

    const xed_iclass_enum_t get_iclass_code() {
        return xed_decoded_inst_get_iclass((const xed_decoded_inst_t*)$self);
    }

    const char* get_category() {
        xed_category_enum_t category = xed_decoded_inst_get_category((const xed_decoded_inst_t*)$self);
        return xed_category_enum_t2str(category);
    }

    const xed_category_enum_t get_category_code() {
        return xed_decoded_inst_get_category((const xed_decoded_inst_t*)$self);
    }

    const unsigned int get_length() {
        return xed_decoded_inst_get_length($self);
    }

    const unsigned int get_operand_width() {
        return xed_decoded_inst_get_operand_width($self)>>3; //divide by 8
    }

    int get_branch_displacement() {
        return xed_decoded_inst_get_branch_displacement($self);
    }

    unsigned int get_immediate_width() {
        return xed_decoded_inst_get_immediate_width($self);
    }

    int32_t get_signed_immediate() {
        return xed_decoded_inst_get_signed_immediate($self);
    }

    uint64_t get_unsigned_immediate() {
        return xed_decoded_inst_get_unsigned_immediate($self);
    }

    uint8_t get_second_immediate() {
        return xed_decoded_inst_get_second_immediate($self);
    }


    // unsigned int get_memory_displacement() {
    //     return xed_decoded_inst_get_memory_displacement($self);
    // }


    %cstring_output_allocate_size(char** bytes, unsigned int* bytes_len, free(*$1));
    void get_bytes(char** bytes, unsigned int* bytes_len) {
        unsigned int length = xed_decoded_inst_get_length($self);
        *bytes  = (char*) malloc(length);
        for (int idx=0; idx < length; ++idx) {
            unsigned char byte = (char)xed_decoded_inst_get_byte($self, idx);
            printf("byte %d\n", byte);
            (*bytes)[idx] = byte;
        }
        *bytes_len = length;
        printf("%d\n", length);
    }
}

%extend inst_list_t {

    xed_decoded_inst_t* __getitem__(int i) {
        if(abs(i) >= $self->size) {
            iter_error = 1;
            return NULL;
        }
        if(i < 0) {
            return $self->inst_array[$self->size+i]; //i is negative
        }
        return $self->inst_array[i];
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

    int is_finished_by_call() {
        return (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_CALL);
    }

    int is_finished_by_branch() {
        return (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_COND_BR)
            || (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_UNCOND_BR)
            || (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_CALL)
            || (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_SYSRET)
            || (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_SYSCALL)
            || (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_SYSTEM)
            || (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_RET);
    }

    int is_finished_by_cond_branch() {
        return (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_COND_BR);
    }

    int is_finished_by_uncond_branch() {
        return (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_UNCOND_BR)
            || (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_CALL);
    }

    int is_finished_by_ret() {
        return (xed_decoded_inst_get_category($self->inst_array[$self->size-1]) == XED_CATEGORY_RET);
    }

    int is_finished_by_direct_branch() {
        if(!inst_list_t_is_finished_by_branch($self)) {
            return 0;
        }
        unsigned int i, noperands;
        xed_decoded_inst_t* xedd = $self->inst_array[$self->size-1];
        const xed_inst_t* xi = xed_decoded_inst_inst(xedd);
        for( i=0; i < noperands ; i++) { 
            const xed_operand_t* op = xed_inst_operand(xi,i);
            xed_operand_enum_t op_name = xed_operand_name(op);
            if(op_name >= XED_OPERAND_REG0 && op_name <= XED_OPERAND_BASE1) {
                return 0;
            }
        }
        return 1;
    }

    int is_finished_by_indirect_branch() {
        if(!inst_list_t_is_finished_by_branch($self)) {
            return 0;
        }
        unsigned int i, noperands;
        xed_decoded_inst_t* xedd = $self->inst_array[$self->size-1];
        const xed_inst_t* xi = xed_decoded_inst_inst(xedd);
        for( i=0; i < noperands ; i++) { 
            const xed_operand_t* op = xed_inst_operand(xi,i);
            xed_operand_enum_t op_name = xed_operand_name(op);
            if(op_name >= XED_OPERAND_REG0 && op_name <= XED_OPERAND_BASE1) {
                return 1;
            }
        }
        return 0;
    }

    uint64_t length() {
        uint64_t ret = 0;
        for(size_t idx=0; idx<inst_list_size($self); ++idx) {
            ret += xed_decoded_inst_get_length($self->inst_array[idx]);
        }
        return ret;
    }

    int64_t get_jump_address() {
        uint64_t block_length = inst_list_t_length($self);
        xed_decoded_inst_t* last_inst = $self->inst_array[$self->size-1];
        int64_t branch_displ = xed_decoded_inst_get_branch_displacement(last_inst);
        if(branch_displ != 0) {
            return branch_displ + block_length + $self->base;
        } else {
            return 0;
        }
    }
/*
    inst_list_t* extend(inst_list_t* rhs) {
        inst_list_extend($self, rhs);
        return $self;
    }

    inst_list_t* __add__(inst_list_t* rhs) {
        inst_list_extend($self, rhs);
        return $self;
    }
*/

    struct inst_list_iter* __iter__() {
        struct inst_list_iter* ret = (struct inst_list_iter*)malloc(sizeof(struct inst_list_iter));
        ret->list = $self;
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