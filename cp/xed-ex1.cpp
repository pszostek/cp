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

//
// usage: ./xed-ex1 [32,64] /path/to/dumped/.text/section
//

int disassemble(int mode, char* data, unsigned int length) {
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
    if (mode == 64) {
        long_mode = true;
    } else if(mode = 32) {
        long_mode = false;
    } else {
        cerr << "Arg #1 must be equal to 32 or 64." << endl;
        return 1;
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
    cout << length << " bytes" << endl;

    if (length == 0) {
        cout << "Must supply non-empty input string" << endl;
        return 2;
    }

    uint32_t start = 0, stop = 1;
    uint32_t inst_count = 0;

    double start_time = omp_get_wtime();
    while(start < length && stop <= length) {
        xed_decoded_inst_zero_set_mode(&xedd, &dstate);
        // cout << "start: " << start << " stop: " << stop << endl;
        //     cout << hex << setw(2) << setfill('0')
        //          << XED_STATIC_CAST(unsigned int,itext[start]) << " ";
        // cout << endl << setfill(' ');
         for(int i=start; i<stop; ++i) {
             cout << hex << setw(2) << XED_STATIC_CAST(unsigned int, data[i]) << " ";
         } cout << endl;

        xed_error_enum_t xed_error = xed_decode(&xedd, 
                                                XED_REINTERPRET_CAST(xed_uint8_t*,data+start),
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
            // cerr << "Could not decode given input: XED general error" << endl;
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
    return 0;
}


int main(int argc, char** argv);

int main(int argc, char** argv) {


    int retcode = disassemble(atoi(argv[1]), argv[3], atoi(argv[2]));
    return retcode;
}
