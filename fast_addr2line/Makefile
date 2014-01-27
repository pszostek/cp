#BEGIN_LEGAL
#Intel Open Source License 
#
#Copyright (c) 2002-2013 Intel Corporation. All rights reserved.
# 
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are
#met:
#
#Redistributions of source code must retain the above copyright notice,
#this list of conditions and the following disclaimer.  Redistributions
#in binary form must reproduce the above copyright notice, this list of
#conditions and the following disclaimer in the documentation and/or
#other materials provided with the distribution.  Neither the name of
#the Intel Corporation nor the names of its contributors may be used to
#endorse or promote products derived from this software without
#specific prior written permission.
# 
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
#ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#END_LEGAL
# Makefile for examples

####################################################################
# External tools
COMPILER=gnu
#COMPILER=ms

SHARED=0
#SHARED=1
ifeq ($(COMPILER),gnu)
  CC  = gcc
  CXX = g++
  CXX_LINKER = $(CXX)
  CC_LINKER = $(CC)
  RM=rm
  OBJEXT=o
  EXEEXT=
  CXXSRCEXT=cpp
  CCSRCEXT=c
  ifeq ($(SHARED),1)
     LIBEXT=so 
 else
     LIBEXT=a
  endif
  LINKOUT=-o 
  OUTOPT=-o 
  COPT=-c
  IOPT=-I
  CXXFLAGS = -MMD -fPIC
  CCFLAGS = -MMD -fPIC

  #
  # Uncomment these next 2 if you want 32b object and executable 
  # files and are on a 64b system. (You must be using the ia32 
  # version of libxed).
  #
  #CCFLAGS += -m32
  #CXXFLAGS += -m32
  CXXFLAGS += -DXED_DWARF


  LDFLAGS  = 

  #The windows library does not work with cygwin, but in general on cygwin,
  # enable these:
  #CXXFLAGS += -mno-cygwin
  #CCFLAGS += -mno-cygwin
  #LDFLAGS += -mno-cygwin
else
  CC  = cl
  CXX = cl
  # you want MSVS's link, not cygwin's link.
  # make sure you move cygwin's /bin/link command out of the way!
  CXX_LINKER = link
  CC_LINKER = link
  RM=rm
  OBJEXT=obj
  EXEEXT=.exe
  CXXSRCEXT=cpp
  CCSRCEXT=c
  LIBEXT=lib
  LINKOUT=/OUT:
  OUTOPT=/Fo
  COPT=/c 
  IOPT=/I
  CXXFLAGS = /nologo /EHsc
  CCFLAGS  = /nologo
  LDFLAGS  = /nologo
endif
###################################################################
CXXFLAGS += $(IOPT)../include 
CCFLAGS  += $(IOPT)../include
LIBXED   = ../lib/libxed.${LIBEXT}
EXTRA_LDLIBS_TARGET = -ldwarf -lelf -lpthread
###################################################################
.PHONY: demos cmdline  clean-examples test-xed

XED = fast_addr2line
XED_SUFFIXED= $(XED:%=%$(EXEEXT))

XED_TEST_APPS = ${XED_SUFFIXED} # ${XED_DEMOS_SUFFIXED} 
all: ${XED_TEST_APPS} addr2line_python
demos: ${XED_DEMOS_SUFFIXED}
cmdline: ${XED_SUFFIXED}

######################################################################

%.${OBJEXT}: %.${CXXSRCEXT}
	${CXX} ${COPT} ${CXXFLAGS}  $< ${OUTOPT}$@
%.${OBJEXT}: %.${CCSRCEXT}
	${CC} ${COPT} ${CCFLAGS}  $< ${OUTOPT}$@

########################################################################
XED_CXX_COMMON_OBJ = xed-examples-ostreams.${OBJEXT} xed-enc-lang.${OBJEXT}
XED_CC_COMMON_OBJ  = xed-examples-util.${OBJEXT}
XED_CC_COMMON_OBJ += xed-dot-prep.${OBJEXT}
XED_CC_COMMON_OBJ += xed-dot.${OBJEXT}

#################################################################

XED_OBJ2 += xed-disas-macho.${OBJEXT}
XED_OBJ2 += xed-disas-pecoff.${OBJEXT}
XED_OBJ2 += xed-disas-raw.${OBJEXT}
XED_OBJ2 += xed-disas-elf.${OBJEXT}
XED_OBJ2 += xed-symbol-table.${OBJEXT} 
XED_OBJ2 += ${XED_CC_COMMON_OBJ} 
XED_OBJ2 += ${XED_CXX_COMMON_OBJ}

#XED_OBJ  = xed.${OBJEXT} 
XED_OBJ += ${XED_OBJ2}

# define DBGHELP=1 on the command line to enable using dbghelp.dll on windows
DBGHELP ?= 0
ifeq ($(DBGHELP),1)
  XED_OBJ += udhelp.${OBJEXT}
  CXXFLAGS += /DXED_DBGHELP
  EXTRA_LDLIBS_TARGET += dbghelp.lib version.lib
endif

demo:
	make
	export LD_LIBRARY_PATH=../lib:${LD_LIBRARY_PATH}
	python -c 'import addr2line as a2l; a2l.initialize_line_numbers("../tests/files/test_elf"); print a2l.find_line_number(0x40080c)'


xed${EXEEXT}: ${XED_OBJ} ${LIBXED}
	${CXX_LINKER}  ${LDFLAGS}  ${LINKOUT}$@ $^ ${EXTRA_LDLIBS_TARGET}

fast_addr2line${EXEEXT}: ${XED_OBJ2} fast_addr2line.${OBJEXT} ${LIBXED}
	${CXX_LINKER}  ${LDFLAGS}  ${LINKOUT}$@ $^ ${EXTRA_LDLIBS_TARGET}

addr2line_python: _addr2line.so addr2line.py

_addr2line.so: addr2line_wrap.cxx fast_addr2line.o ${XED_OBJ}
	g++ -fPIC $^ -I/usr/include/python2.7 -L/home/paszoste/cp/pin-example/lib -L../lib -ldwarf -lelf -lxed -I../include -shared -o $@

addr2line.py addr2line_wrap.cxx: addr2line.i fast_addr2line.h
	swig -c++ -Dinline= -Wall -python $< 

#################################################################

clean:
	-${RM} *.o *.obj  *.d *.exe > /dev/null 2>&1
	-${RM} ${XED_TEST_APPS} > /dev/null 2>&1
	-${RM} -f addr2line.pyc addr2line_wrap.cxx _addr2line.so addr2line.py 2>&1

.PHONY: clean demo

#################################################################
-include *.d
