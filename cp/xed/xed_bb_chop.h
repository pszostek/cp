#ifdef __cplusplus
extern "C" {
#endif
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <unistd.h>
#include "xed_disass.h"
#include "xed-category-enum.h"
#include "xed-decoded-inst.h"
#ifdef __cplusplus
}
#endif
#include <list>


#ifndef _XED_BB_CHOP_
#define _XED_BB_CHOP_

typedef enum {PLT,
              INIT,
              FINI,
              TEXT,
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

std::list<bb_t> detect_basic_blocks(char* elf_data, unsigned int fsize);

#endif