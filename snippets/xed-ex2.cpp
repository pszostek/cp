extern "C" {
#include "include/xed-interface.h"
}
#include <iostream>
#include <iomanip>
#include <omp.h>
#include <sstream>
#include <cassert>
#include <cstring>
#include <cstdlib>
#include <cstdio>
using namespace std;

int main(int argc, char** argv);

int main(int argc, char** argv) {
    xed_bool_t long_mode;
    xed_state_t dstate;
    int first_argv;
    int bytes;
    int i;
    unsigned int u;
    xed_decoded_inst_t xedd;
#define BUFLEN  1000
    char* buf = (char*)malloc(atoi(argv[2])*sizeof(char)+1);
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
    char buffer[BUFLEN];

    xed_tables_init();
    xed_state_zero(&dstate);
    xed_set_verbosity( 99 );

    if (argc != 4) {
        cerr << "3 arguments must be supplied." << endl;
        exit(1);
    }

    if (argc > 2 && strcmp(argv[1], "64") == 0) {
        long_mode = true;
    } else if(strcmp(argv[1], "32") == 0) {
        long_mode = false;
    } else {
        cerr << "Arg #1 must be equal to 32 or 64." << endl;
        exit(1);
    }

    bytes = atoi(argv[2]);
    cout << "bytes " << bytes << " long mode " << long_mode << endl;
    uint32_t start=0, stop=1;
    uint32_t inst_count = 0;

     while(start < bytes && stop <= bytes) {
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

        xed_error_enum_t xed_error = xed_decode(&xedd, 
                                                XED_REINTERPRET_CAST(xed_uint8_t*,buf+start),
                                                stop-start);
        switch(xed_error)
        {
          case XED_ERROR_NONE:
            xed_decoded_inst_dump_att_format(&xedd,buffer,BUFLEN, 1231);
            cout << buffer << endl;
            inst_count++;
            start = stop;
            stop = start+1;
            break;
          case XED_ERROR_BUFFER_TOO_SHORT:
            // cerr << "Not enough bytes provided" << endl;
            stop++;
            break;
          case XED_ERROR_GENERAL_ERROR:
            // cerr << "Could not decode given input." << endl;
            stop++;
             break;
          default:
            // cerr << "Unhandled error code " << xed_error_enum_t2str(xed_error) << endl;
            stop++;
            break;
        }

    }

    // xed_bool_t ok;
    // for(u=  XED_SYNTAX_XED; u < XED_SYNTAX_LAST; u++) {
    //     xed_syntax_enum_t syntax = static_cast<xed_syntax_enum_t>(u);
    //     ok = xed_format(syntax, &xedd, buffer, BUFLEN, 0);
    //     if (ok)
    //         cout << xed_syntax_enum_t2str(syntax) << " syntax: "  << buffer << endl;
    //     else
    //         cout << "Error disassembling " << xed_syntax_enum_t2str(syntax) << " syntax" << endl;
    // }
    // return 0;
}
