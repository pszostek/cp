
#ifdef __cplusplus
extern "C" {
#endif

#include "xed-interface.h"
#include <stddef.h>

#ifdef __cplusplus
}
#endif


#ifndef _XED_DISASS_H_
#define _XED_DISASS_H_

#define INST_LIST_INIT_CAPACITY 32

typedef struct {
    unsigned long long base; 
    size_t size;
    size_t capacity;
    xed_decoded_inst_t** inst_array;
} inst_list_t;

void inst_list_init_size(inst_list_t*, size_t size);
void inst_list_init(inst_list_t*, unsigned long long base);
void inst_list_delete(inst_list_t*);
void inst_list_resize(inst_list_t*, size_t new_capacity);
size_t inst_list_size(inst_list_t*);
xed_decoded_inst_t* inst_list_get(inst_list_t*, size_t);
unsigned int inst_list_append(inst_list_t*, xed_decoded_inst_t*);
//unsigned int inst_list_extend(inst_list_t* lhs, inst_list_t* rhs);

int terminates_bb(xed_decoded_inst_t*);

inst_list_t* _disassemble_x86(char* data, unsigned length, unsigned base);
inst_list_t* _disassemble_x64(char* data, unsigned length, unsigned base);
inst_list_t* _disassemble(xed_state_t xed_state, char* data, unsigned length, unsigned base);

inst_list_t* _disassemble_x86_until_bb_end(char* data, unsigned length, unsigned base);
inst_list_t* _disassemble_x64_until_bb_end(char* data, unsigned length, unsigned base);
inst_list_t* _disassemble_until_bb_end(xed_state_t xed_state, char* data, unsigned length, unsigned base);

#endif
