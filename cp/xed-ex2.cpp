/*BEGIN_LEGAL 
Intel Open Source License 

Copyright (c) 2002-2013 Intel Corporation. All rights reserved.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.  Redistributions
in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.  Neither the name of
the Intel Corporation nor the names of its contributors may be used to
endorse or promote products derived from this software without
specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
END_LEGAL */
/// @file xed-ex2.cpp

// decoder example. C++ version of xed-ex4.c

extern "C" {
#include "xed-interface.h"
}
#include <iostream>
#include <iomanip>
#include <sstream>
#include <cassert>
#include <cstring>
#include <cstdlib>
using namespace std;

int main(int argc, char** argv);

int main(int argc, char** argv) {
    xed_bool_t long_mode = false;
    xed_state_t dstate;
    int first_argv;
    int bytes = 0;
    unsigned char itext[argc];
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
        first_argv = 2;
    } else {
        first_argv = 1;
    }



    for( i=first_argv ;i < argc; i++)  {
        unsigned int x;
        istringstream s(argv[i]);
        s >> hex >> x;

        itext[bytes++] = XED_STATIC_CAST(xed_uint8_t,x);
    }
    if (bytes == 0) {
        cout << "Must supply some hex bytes" << endl;
        exit(1);
    }


    uint32_t start=0, stop=1;
    uint32_t inst_count = 0;

     while(start < argc && stop <= argc-2) {
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
                                                XED_REINTERPRET_CAST(xed_uint8_t*,itext+start),
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
    cout << inst_count << endl;
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
