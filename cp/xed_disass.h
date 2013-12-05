#ifdef __cplusplus
extern "C" {
#endif

#include "include/xed-interface.h"

#ifdef __cplusplus
}
#endif

#ifndef _XED_DISASS_H
#define _XED_DISASS_H


#define MODE32 0
#define MODE64 1

typedef struct {
    size_t memory_allocated;
    size_t inst_count;
    xed_decoded_inst_t* inst;
} inst_list_t;


void inst_list_init(inst_list_t*);
void inst_list_delete(inst_list_t*);
unsigned int inst_list_append(inst_list_t*, xed_decoded_inst_t);
void print_operand_width(const xed_decoded_inst_t* p);

inst_list_t* disassemble(int mode, char* data, unsigned int length);

#endif