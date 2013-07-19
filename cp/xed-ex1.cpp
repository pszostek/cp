extern "C" {
#include "xed-interface.h"
}
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <cassert>
#include <cstring>
#include <omp.h>
#include <cstdlib>
using namespace std;

int main(int argc, char** argv);

int main(int argc, char** argv) {
    xed_bool_t long_mode;
    xed_state_t dstate;
    int first_argv;
    int bytes = 0;
    int i;
    unsigned int u;
    xed_decoded_inst_t xedd;
#define BUFLEN  1000
    char buffer[BUFLEN];

    xed_tables_init();
    xed_state_zero(&dstate);
    xed_set_verbosity( 99 );

    if (argc > 2 && strcmp(argv[1], "64") == 0) {
        long_mode = true;
    } else if(strcmp(argv[1], "32") == 0) {
        long_mode = false;
    } else {
        cerr << "Arg #1 must be equal to 32 or 64." << endl;
        exit(1);
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

    // read .text section from a file
    ifstream input_file;

    input_file.open(argv[2], ifstream::in | ifstream::binary);
    input_file.seekg (0, input_file.end);
    bytes = input_file.tellg();
    input_file.seekg (0, input_file.beg);

    cout << bytes << " bytes" << endl;

    if (bytes == 0) {
        cout << "Must supply non-empty input file" << endl;
        exit(1);
    }
    xed_uint8_t *itext = (xed_uint8_t*) malloc(bytes);
    if(itext == NULL) {
        exit(2);
    }
    input_file.read((char*)(itext), bytes);

    uint32_t start = 0, stop = 1;
    uint32_t inst_count = 0;

    double start_time = omp_get_wtime();
    while(start < bytes && stop <= bytes) {
        xed_decoded_inst_zero_set_mode(&xedd, &dstate);
        // cout << "start: " << start << " stop: " << stop << endl;
        //     cout << hex << setw(2) << setfill('0')
        //          << XED_STATIC_CAST(unsigned int,itext[start]) << " ";
        // cout << endl << setfill(' ');
         // for(int i=start; i<stop; ++i) {
         //     cout << hex << setw(2) << XED_STATIC_CAST(unsigned int, itext[i]) << " ";
         // } cout << endl;

        xed_error_enum_t xed_error = xed_decode(&xedd, 
                                                XED_REINTERPRET_CAST(xed_uint8_t*,itext+start),
                                                stop-start);
        switch(xed_error)
        {
          case XED_ERROR_NONE:
            xed_decoded_inst_dump_intel_format(&xedd,buffer,BUFLEN, 1);
            cout << buffer << endl;
            inst_count++;
            start = stop;
            stop = start + 1;
            break;
          case XED_ERROR_BUFFER_TOO_SHORT:
             // cerr << "Not enough bytes provided" << endl;
            stop += 1;
            break;
          case XED_ERROR_GENERAL_ERROR:
            cerr << "Could not decode given input: XED general error" << endl;
            stop += 1;
            break;
          default:
            // cerr << "Unhandled error code " << xed_error_enum_t2str(xed_error) << endl;
            stop += 1;
            break;
        }

    }

    double end_time = omp_get_wtime();
    cout << inst_count << " instructions" << endl;  
    cout << end_time - start_time << " seconds" << endl;
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
