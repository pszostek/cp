#include <stdlib.h>
#include <stdio.h>
#include "xed_disass.h"

int main(int argc, char** argv) {
    char* buf;
    size_t file_length;
    char line[64];
    size_t idx;
    FILE* fp = fopen(argv[1], "r");
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
    inst_list_t* list = _disassemble_x64_until_bb_end(buf, file_length, 0);
    inst_list_t* list1 = _disassemble_x64_until_bb_end(buf, file_length, 0);

   // inst_list_extend(list, list1);
    // printf("length %zu\n", list->size);
     for(idx=0; idx< list->size; ++idx) {
       xed_decoded_inst_t* inst = list->inst_array[idx];
       xed_decoded_inst_dump_intel_format(inst, line, 64, 0);
       printf("%s %d\n", line, xed_decoded_inst_get_category(inst));
     }
    printf("%zu\n", list->size);
    inst_list_delete(list);
    printf("%zi\n", list1->size);
    inst_list_delete(list1);
    free(buf);
    return 0;
}
