#include "demangle.h"
%module demangle
%{
extern char * cplus_demangle (const char *mangled, int options);
%}

extern char * cplus_demangle (const char *mangled, int options);
