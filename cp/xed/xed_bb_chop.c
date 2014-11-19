#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "xed_disass.h"
#include "xed-category-enum.h"

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
  
} bb_t;

int main(int argc, char** argv) {
    char* buf;
    size_t file_length;
    char line[64];
    size_t idx;
    FILE* fp = fopen(argv[1], "r");
    
    uint64_t *bbs = calloc(sizeof(uint64_t), 1000000);

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

    uint64_t text_base = 0x2c00, start = text_base, stop = start + 1, text_len=0x1039c;
    uint64_t jaddr = 0;
    int i = start, j = 0;

    xed_decoded_inst_t* xedd = (xed_decoded_inst_t*) malloc(sizeof(xed_decoded_inst_t));
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    xed_error_enum_t xed_error;
    
    xed_tables_init();

    bbs[j++] = start;    
    while(stop<=text_base+text_len) {
      printf("%d ", i-start);
      xed_decoded_inst_zero_set_mode(xedd, &dstate);	// WHY?
      xed_error = xed_decode(xedd, 
          XED_REINTERPRET_CAST(xed_uint8_t*,buf+start),
          stop-start);

      switch(xed_error) {
          case XED_ERROR_NONE:
              if(terminates_bb(xedd)) {
                  jaddr = xed_decoded_inst_get_branch_displacement(xedd) + i + 1;
                  printf("Bing! 0x%x -> 0x%x; next bb: 0x%x\n", start, jaddr, i+1);
                  bbs[j++] = i+1;
                  bbs[j++] = jaddr;
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
    
    int qcomp(const void *a, const void *b) { return *(uint64_t *)a-*(uint64_t *)b; }
    qsort(bbs, j, sizeof(uint64_t), qcomp);
    int k = 0, ctr = 0;
    for (k=0; k<j; k++) {
      if(bbs[k] != bbs[ctr]) bbs[++ctr] = bbs[k];
    }
    printf("\nGathered %d addresses\n", ctr);
    for (k=0; k<ctr+1; k++) {
      printf("\t0x%x\n", bbs[k]);
    }
    return 0;
}
