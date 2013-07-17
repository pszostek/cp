// decoder example. C++ version of xed-ex4.c

extern "C" {
#include "xed-interface.h"
}
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cassert>
#include <cstring>
#include <omp.h>
#include <cstdlib>
using namespace std;

int main(int argc, char** argv);

int main(int argc, char** argv) {
    xed_bool_t long_mode = false;
    xed_state_t dstate;
    int first_argv;
    int bytes = 0;
    unsigned char itext[argc+3];
    int i;
    unsigned int u;
    xed_decoded_inst_t xedd;
#define BUFLEN  1000
    char buffer[BUFLEN];

    xed_tables_init();
    xed_state_zero(&dstate);
    xed_set_verbosity( 99 );

    if (argc > 2 && strcmp(argv[1], "-64") == 0) {
        long_mode = true;
        cout << "LONG" << endl;
    }

    if (long_mode)  {
        dstate.mmode=XED_MACHINE_MODE_LONG_64;
    }
    else {
        xed_state_init(&dstate,
                       XED_MACHINE_MODE_LEGACY_32, 
                       XED_ADDRESS_WIDTH_32b, 
                       XED_ADDRESS_WIDTH_32b);
    }
    for( i=3 ;i < argc; i++)  {
        unsigned int x;
        istringstream s(argv[i]);
        s >> hex >> x;

        // assert(bytes < XED_MAX_INSTRUCTION_BYTES);
        itext[bytes++] = XED_STATIC_CAST(xed_uint8_t,x);
    }
    if (bytes == 0) {
        cout << "Must supply some hex bytes" << endl;
        exit(1);
    }

 //   cout << "bytes " << bytes << endl;
    uint32_t start = 0, stop = 1;
    double start_time = omp_get_wtime();
    while(start < bytes && stop <= bytes) {
        xed_decoded_inst_zero_set_mode(&xedd, &dstate);
        // cout << "start: " << start << " stop: " << stop << endl;
        //     cout << hex << setw(2) << setfill('0')
        //          << XED_STATIC_CAST(unsigned int,itext[start]) << " ";
        // cout << endl << setfill(' ');

        xed_error_enum_t xed_error = xed_decode(&xedd, 
                                                XED_REINTERPRET_CAST(xed_uint8_t*,itext+start),
                                                stop-start);
        switch(xed_error)
        {
          case XED_ERROR_NONE:
              xed_decoded_inst_dump_att_format(&xedd,buffer,BUFLEN, 1);
           //   cout << buffer << endl;
              start = stop;
              stop = start + 1;
              break;
          case XED_ERROR_BUFFER_TOO_SHORT:
            // cout << "Not enough bytes provided" << endl;
            stop += 1;
            break;
          case XED_ERROR_GENERAL_ERROR:
            // cout << "Could not decode given input." << endl;
            stop += 1;
            break;
          default:
            // cout << "Unhandled error code " << xed_error_enum_t2str(xed_error) << endl;
            stop += 1;
            break;
        }

    }

    double end_time = omp_get_wtime();
    cout << end_time - start_time << endl;
    // xed_bool_t ok;
    // for(u=  XED_SYNTAX_XED; u < XED_SYNTAX_LAST; u++) {
    //     xed_syntax_enum_t syntax = static_cast<xed_syntax_enum_t>(u);
    //     ok = xed_format(syntax, &xedd, buffer, BUFLEN, 0);
    //     if (ok)
    //         cout << xed_syntax_enum_t2str(syntax) << " syntax: "  << buffer << endl;
    //     else
    //         cout << "Error disassembling " << xed_syntax_enum_t2str(syntax) << " syntax" << endl;
    // }
    return 0;
}
