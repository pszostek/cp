#ifdef __cplusplus
extern "C" {
#endif
#include "xed_disass.h"
#include "xed-category-enum.h"
#include "xed-decoded-inst.h"
#ifdef __cplusplus
}
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <cstddef>
#include <sys/types.h>
//#include <unistd.h>
#include <vector>
#endif

//typedef unsigned long long uint64_t;
//typedef unsigned uint32_t;

#ifndef _XED_BB_CHOP_
#define _XED_BB_CHOP_

typedef enum {INIT,
              PLT,
              TEXT,
              FINI,
              NUMBER_OF_SECTIONS} ELF_SECTION;

typedef struct {
  uint32_t addr;
  uint32_t target;
  char direct;
  char conditional;
  char isjump;
} jump_t;

typedef struct {
  uint32_t addr;
  uint16_t ilen;
  uint16_t len;
  ELF_SECTION section;
  jump_t jump;
} bb_t;

typedef struct {
  uint32_t start;
  uint16_t len;
  uint32_t end;
} bbnowak_t;

std::vector<unsigned long> new_detect_static_basic_blocks(char* elf_data, unsigned int fsize);
std::vector<bbnowak_t> newer_detect_static_basic_blocks(char* elf_data, unsigned int fsize);
std::vector<bb_t> detect_static_basic_blocks(char* elf_data, unsigned int fsize);
std::vector<int> test();

#endif

