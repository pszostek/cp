#include "demangle.h"
%module demangle
%{
extern char * cplus_demangle (const char *mangled, int options);
%}

extern char * cplus_demangle (const char *mangled, int options);

%inline %{
char * demangle(const char* mangled) {
        return cplus_demangle(mangled, 0);
    };
%}
