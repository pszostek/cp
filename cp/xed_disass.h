#include "include/xed-interface.h"

#if !defined(_XED_DISASS_H_)
#define _XED_DISASS_H

#define INST_LIST_INIT_CAPACITY 32

typedef struct {
    size_t size;
    size_t capacity;
    xed_decoded_inst_t* inst_array;
} inst_list_t;

typedef enum {
    MODE_X86, MODE_X64
} binary_mode_t;


void inst_list_init_size(inst_list_t*, size_t size);
void inst_list_init(inst_list_t*);
void inst_list_delete(inst_list_t*);
void inst_list_resize(inst_list_t*, size_t new_capacity);
size_t inst_list_size(inst_list_t*);
xed_decoded_inst_t inst_list_get(inst_list_t*, size_t);
unsigned int inst_list_append(inst_list_t*, xed_decoded_inst_t);
int terminates_bb(xed_decoded_inst_t*);
void print_operand_width(const xed_decoded_inst_t* p);

inst_list_t* disassemble(binary_mode_t mode, char* data, unsigned int length);
inst_list_t* disassemble_until_bb_end(binary_mode_t mode, char* data, unsigned int length);

#endif