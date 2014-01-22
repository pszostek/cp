#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "xed_disass.h"
#include "include/xed-category-enum.h"

int terminates_bb(xed_decoded_inst_t* inst) {
    xed_category_enum_t category = xed_decoded_inst_get_category(inst);
    return (category == XED_CATEGORY_CALL) ||
           (category == XED_CATEGORY_RET) ||
           (category == XED_CATEGORY_SYSCALL) ||
           (category == XED_CATEGORY_SYSRET) ||
           (category == XED_CATEGORY_SYSTEM) ||
           (category == XED_CATEGORY_UNCOND_BR) ||
           (category == XED_CATEGORY_COND_BR);

}

typedef struct {
  uint64_t addr;
  uint64_t target;
  uint16_t ilen;
  uint16_t len;
  char direct;
  char conditional;
  char isjump;
} bb_t;

int main(int argc, char** argv) {
    char* buf;
    size_t file_length;
    size_t idx;
    FILE* fp = fopen(argv[1], "r");
    
//    uint64_t *bbs = calloc(sizeof(uint64_t), 1000000);
    bb_t *bbs = calloc(sizeof(bb_t), 1000000);
    bb_t *jumps = calloc(sizeof(bb_t), 1000000);

    if(fp != NULL) {
      fseek(fp, 0, SEEK_END);
      file_length = ftell(fp);
      buf = (char*)malloc(file_length+1);
      fseek(fp, 0, SEEK_SET);
      size_t newLen = fread(buf, sizeof(char), file_length, fp);
      printf("file length %zu, read %zu\n", file_length, newLen);
      if (newLen == 0) {
        fputs("Error reading file", stderr);
      } else {
        buf[newLen] = '\0';
      }
      fclose(fp);
    } else {
      printf("can't open file\n");
      return 1;
    }

    // TODO: need to disasm both text and plt
    uint64_t text_base = 0x2c00, start = text_base, stop = start + 1, text_len=0x1039c;
    uint64_t jaddr = 0;
    int i = start, j = 0, m = 0;

    xed_decoded_inst_t* xedd = (xed_decoded_inst_t*) malloc(sizeof(xed_decoded_inst_t));
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    xed_error_enum_t xed_error;
    
    xed_tables_init();

    bbs[j++].addr = start;    
    while(stop<=text_base+text_len) {
      printf("%d ", i-start);
      xed_decoded_inst_zero_set_mode(xedd, &dstate);	// WHY?
      xed_error = xed_decode(xedd, 
          XED_REINTERPRET_CAST(xed_uint8_t*,buf+start),
          stop-start);

      switch(xed_error) {
          case XED_ERROR_NONE:
              if(terminates_bb(xedd)) {
                  jaddr = xed_decoded_inst_get_branch_displacement(xedd) ?
                      xed_decoded_inst_get_branch_displacement(xedd) + i + 1 :
                      0;
                  printf("Bing! 0x%x -> 0x%x; next bb: 0x%x\n", start, jaddr, i+1);
                  bbs[j++].addr = i+1;
                  if (jaddr) bbs[j++].addr = jaddr;

                  jumps[m].addr = start;
                  jumps[m].target = jaddr;
                  jumps[m].isjump = 1;
                  jumps[m].conditional = (xed_decoded_inst_get_category(xedd) == XED_CATEGORY_COND_BR);
                  jumps[m].direct = jumps[m].conditional && (jaddr > 0);
                  m++;
              }
              start = stop;
              stop = start + 1;
              break;

          case XED_ERROR_BUFFER_TOO_SHORT:
          case XED_ERROR_GENERAL_ERROR:
          default:
              stop += 1;
      }
        
      i++;
    }

    free(buf);
    
    int qcomp(const void *a, const void *b) { return (((bb_t *)a)->addr)-(((bb_t *)b)->addr); }
    qsort(bbs, j, sizeof(bb_t), qcomp);
    int k = 0, ctr = 0;
    for (k=0; k<j; k++) {
      if(bbs[k].addr != bbs[ctr].addr) bbs[++ctr] = bbs[k];
    }
    int num_bbs = ctr;
    int num_jumps = m;

    qsort(jumps, m, sizeof(bb_t), qcomp);    
    printf("\nGathered %d jumps\n", num_jumps);
    for(k=0; k<num_jumps; k++) printf("\t0x%x->0x%x\n", jumps[k].addr, jumps[k].target);

    k = 0, ctr = 0;
    while(jumps[ctr].addr < bbs[0].addr) ctr++;
    for (k=0; k<num_bbs+1; k++) {
      if(bbs[k+1].addr > jumps[ctr].addr) {
          bbs[k].target = jumps[ctr].target;
          bbs[k].isjump = jumps[ctr].isjump;
          bbs[k].conditional = jumps[ctr].conditional;
          bbs[k].direct = jumps[ctr].direct;
          ctr++;
      }
    }

    printf("\nGathered %d addresses and %d jumps\n", num_bbs, num_jumps);
    printf("\t%16s %3s   %16s %3s %3s\n",
        "Address",
        "BRA",
        "Target",
        "CON",
        "DIR");        
    for (k=0; k<num_bbs+1; k++) {
      printf("\t%16p %3s ->%16x %3s %3s\n", 
          bbs[k].addr, 
          bbs[k].isjump ? "YES" : " NO", 
          bbs[k].target,
          bbs[k].conditional ? "YES" : " NO",
          bbs[k].direct ? "YES" : " NO");
    }
    return 0;
}


/*
SWIGINTERN int inst_list_t_is_finished_by_call(inst_list_t *self){
        return (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_CALL);
    }
SWIGINTERN int inst_list_t_is_finished_by_branch(inst_list_t *self){
        return (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_COND_BR)
            || (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_UNCOND_BR)
            || (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_CALL)
            || (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_SYSRET)
            || (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_SYSCALL)
            || (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_SYSTEM)
            || (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_RET);
    }
SWIGINTERN int inst_list_t_is_finished_by_cond_branch(inst_list_t *self){
        return (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_COND_BR);
    }
SWIGINTERN int inst_list_t_is_finished_by_uncond_branch(inst_list_t *self){
        return (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_UNCOND_BR)
            || (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_CALL);
    }
SWIGINTERN int inst_list_t_is_finished_by_ret(inst_list_t *self){
        return (xed_decoded_inst_get_category(self->inst_array[self->size-1]) == XED_CATEGORY_RET);
    }
SWIGINTERN int inst_list_t_is_finished_by_direct_branch(inst_list_t *self){
        if(!inst_list_t_is_finished_by_branch(self)) {
            return 0;
        }
        unsigned int i, noperands;
        xed_decoded_inst_t* xedd = self->inst_array[self->size-1];
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
SWIGINTERN int inst_list_t_is_finished_by_indirect_branch(inst_list_t *self){
        if(!inst_list_t_is_finished_by_branch(self)) {
            return 0;
        }
        unsigned int i, noperands;
        xed_decoded_inst_t* xedd = self->inst_array[self->size-1];
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
*/
