#!/usr/bin/env bash

source /afs/cern.ch/sw/lcg/external/gcc/5.2.0/x86_64-slc6/setup.sh
source ~/cp/bin/activate

export LD_LIBRARY_PATH=$PWD/gui/hierarchical_header/libhhv/:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$PWD/../lib:$LD_LIBRARY_PATH
