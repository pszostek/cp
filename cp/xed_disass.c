
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "xed_disass.h"

#define TRUE 1
#define FALSE 0

void inst_list_init(inst_list_t* inst_list) {
  size_t memory_needed = 32*sizeof(xed_decoded_inst_t);
  inst_list->inst = (xed_decoded_inst_t*)malloc(memory_needed);
  if (inst_list->inst == NULL) {
    puts("Error allocating memory");
    exit(1);
  }
  inst_list->memory_allocated = memory_needed;
  inst_list->inst_count = 0;
}

unsigned int inst_list_append(inst_list_t* inst_list, xed_decoded_inst_t inst) {
  if(inst_list->memory_allocated/sizeof(xed_decoded_inst_t) > inst_list->inst_count) {

    inst_list->inst[inst_list->inst_count++] = inst;
  } else {
    size_t mem = inst_list->memory_allocated*2;
    xed_decoded_inst_t* new_inst_array = (xed_decoded_inst_t*)realloc(inst_list->inst, mem);
    if(new_inst_array == NULL) {
      free(inst_list->inst);
      exit(1);
    }
    inst_list->inst = new_inst_array;
    inst_list->memory_allocated = mem;
  }
  return inst_list->inst_count;
}

void inst_list_delete(inst_list_t* inst_list) {
  free(inst_list->inst);
}

inst_list_t* disassemble(int mode, char* data, unsigned int length) {
    xed_bool_t long_mode;
    xed_state_t dstate;
    int first_argv;
    int i;
    unsigned int u;
        xed_decoded_inst_t xedd;
    const unsigned int BUFLEN = 1000;
    char buffer[BUFLEN];

    xed_tables_init();
    xed_state_zero(&dstate);
    xed_set_verbosity( 99 );
    if (mode == MODE64) {
        long_mode = TRUE;
    } else if(mode == MODE32) {
        long_mode = FALSE;
    } else {
        fprintf(stderr, "Arg #1 must be equal to 32 or 64.");
        return NULL;
    }


    if (length == 0) {
        fprintf(stderr, "Must supply non-empty input string");
        return NULL;
    }

    uint32_t start = 0, stop = 1;
    uint32_t inst_count = 0;
    inst_list_t* ret = (inst_list_t*) malloc(sizeof(inst_list_t));
    inst_list_init(ret);
   // double start_time = omp_get_wtime();
    while(start < length && stop <= length) {

    if (long_mode)  {
        dstate.mmode=XED_MACHINE_MODE_LONG_64;
    }
    else {
        xed_state_init(&dstate,
                       XED_MACHINE_MODE_LEGACY_32, 
                       XED_ADDRESS_WIDTH_32b, 
                       XED_ADDRESS_WIDTH_32b);
    }
        xed_decoded_inst_zero_set_mode(&xedd, &dstate);
       //  for(int i=start; i<stop; ++i) {
       //      cout << hex << setw(2) << XED_STATIC_CAST(unsigned int, data[i]) << " ";
       //  } cout << endl;

        xed_error_enum_t xed_error = xed_decode(&xedd, 
                                                XED_REINTERPRET_CAST(xed_uint8_t*,data+start),
                                                stop-start);

        switch(xed_error)
        {
          case XED_ERROR_NONE:
              inst_list_append(ret, xedd);
              //xed_decoded_inst_dump_att_format(&xedd,buffer,BUFLEN, 1231);
            inst_count++;
            start = stop;
            stop = start + 1;
            break;
          case XED_ERROR_BUFFER_TOO_SHORT:
             // cerr << "Not enough bytes provided" << endl;
            stop += 1;
            break;
          case XED_ERROR_GENERAL_ERROR:
            // cerr << "Could not decode given input: XED general error" << endl;
            stop += 1;
            break;
          default:
            // cerr << "Unhandled error code " << xed_error_enum_t2str(xed_error) << endl;
            stop += 1;
            break;
        }

    }

    return ret;
}

void print_operand_width(const xed_decoded_inst_t* p) {
  printf("%d\n", xed_decoded_inst_get_operand_width(p));
}

int main(int argc, char** argv) {
    char* buf = (char*)malloc(atoi(argv[2])+1);
    FILE* fp = fopen(argv[3], "r");
    if(fp != NULL) {
      size_t newLen = fread(buf, sizeof(char), atoi(argv[2]), fp);
      if (newLen == 0) {
        fputs("Error reading file", stderr);
      } else {
        buf[++newLen] = '\0';
      }
      fclose(fp);
    }

    inst_list_t* list = disassemble(atoi(argv[1]), buf, atoi(argv[2]));
    print_operand_width(list->inst+0);
    return 0;
}