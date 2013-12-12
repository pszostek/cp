
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "xed_disass.h"
#include "include/xed-category-enum.h"

#define TRUE 1
#define FALSE 0

void inst_list_init_size(inst_list_t* inst_list, size_t initial_size) {
  size_t memory_needed = sizeof(xed_decoded_inst_t)*initial_size;
  inst_list->inst_array = (xed_decoded_inst_t*)malloc(memory_needed);
  if (inst_list->inst_array == NULL) {
    fputs("Error allocating memory!\n", stderr);
    exit(1);
  }
  inst_list->capacity = INST_LIST_INIT_CAPACITY;
  inst_list->size = 0;
}

void inst_list_init(inst_list_t* inst_list) {
  return inst_list_init_size(inst_list, INST_LIST_INIT_CAPACITY);
}

xed_decoded_inst_t inst_list_get(inst_list_t* list, size_t idx) {
  return list->inst_array[idx];
}

unsigned int inst_list_append(inst_list_t* inst_list, xed_decoded_inst_t inst) {
  if(inst_list->size == inst_list->capacity) {
    inst_list_resize(inst_list, inst_list->capacity*2+1);
  }
  inst_list->inst_array[inst_list->size++] = inst;
  return inst_list->size;
}

size_t inst_list_size(inst_list_t* list) {
  return list->size;
}

void inst_list_resize(inst_list_t* inst_list, size_t new_capacity) {
    xed_decoded_inst_t* new_inst_array = 
          (xed_decoded_inst_t*)realloc(inst_list->inst_array, sizeof(xed_decoded_inst_t)*new_capacity);
    if(new_inst_array == NULL) {
      fputs("Error reallocating memory!\n", stderr);
      free(inst_list->inst_array);
      exit(1);
    }
    inst_list->inst_array = new_inst_array;
    inst_list->capacity = new_capacity;
}

void inst_list_delete(inst_list_t* inst_list) {
  free(inst_list->inst_array);
}

inst_list_t* _disassemble(xed_state_t xed_state, char* data, unsigned int length) {
    xed_decoded_inst_t xedd;

    xed_tables_init();

    uint32_t start = 0, stop = 1;
    uint32_t inst_count = 0;
    inst_list_t* ret = (inst_list_t*) malloc(sizeof(inst_list_t));
    inst_list_init(ret);

    while(start < length && stop <= length) {
        xed_decoded_inst_zero_set_mode(&xedd, &xed_state);
        xed_error_enum_t xed_error = xed_decode(&xedd, 
            XED_REINTERPRET_CAST(xed_uint8_t*,data+start),
            stop-start);

        switch(xed_error) {
            case XED_ERROR_NONE:
                inst_list_append(ret, xedd);
                inst_count++;
                start = stop;
                stop = start + 1;
                break;
            case XED_ERROR_BUFFER_TOO_SHORT:
            case XED_ERROR_GENERAL_ERROR:
            default:
                stop += 1;
        }
    }

  return ret;
}

inst_list_t* disassemble_x64(char* data, unsigned int length) {
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    return _disassemble(dstate, data, length);
}

inst_list_t* disassemble_x86(char* data, unsigned int length) {
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
       XED_MACHINE_MODE_LEGACY_32, 
       XED_ADDRESS_WIDTH_32b, 
       XED_ADDRESS_WIDTH_32b);
    return _disassemble(dstate, data, length);
}

inst_list_t* disassemble_x86_until_bb_end(char* data, unsigned int length) {
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
       XED_MACHINE_MODE_LEGACY_32, 
       XED_ADDRESS_WIDTH_32b, 
       XED_ADDRESS_WIDTH_32b);
    return _disassemble_until_bb_end(dstate, data, length);
}

inst_list_t* disassemble_x64_until_bb_end(char* data, unsigned int length) {
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    return _disassemble_until_bb_end(dstate, data, length);
}

inst_list_t* _disassemble_until_bb_end(xed_state_t xed_state, char* data, unsigned int length) {
    xed_decoded_inst_t xedd;

    xed_tables_init();

    uint32_t start = 0, stop = 1;
    uint32_t inst_count = 0;
    inst_list_t* ret = (inst_list_t*) malloc(sizeof(inst_list_t));
    inst_list_init(ret);

    while(start < length && stop <= length) {
        xed_decoded_inst_zero_set_mode(&xedd, &xed_state);
        xed_error_enum_t xed_error = xed_decode(&xedd, 
            XED_REINTERPRET_CAST(xed_uint8_t*,data+start),
            stop-start);

        switch(xed_error) {
            case XED_ERROR_NONE:
                inst_list_append(ret, xedd);
                inst_count++;
                start = stop;
                stop = start + 1;
                if(terminates_bb(&xedd)) {
                    return ret;
                }
                break;
            case XED_ERROR_BUFFER_TOO_SHORT:
            case XED_ERROR_GENERAL_ERROR:
            default:
                stop += 1;
        }
    }

  return ret;
}

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
    inst_list_t* list = disassemble_x64_until_bb_end(buf, file_length);
    printf("length %zu\n", list->size);
    for(idx=0; idx< list->size; ++idx) {
      xed_decoded_inst_t inst = list->inst_array[idx];
      xed_decoded_inst_dump_intel_format(&inst, line, 64, 0);
      printf("%s %d\n", line, xed_decoded_inst_get_category(&inst));
     // printf("cat %d\n", xed_decoded_inst_get_category(&inst));
    }
    inst_list_delete(list);
    free(buf);
    free(list);
    return 0;
}
