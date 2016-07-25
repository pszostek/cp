#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <unistd.h>
#include "xed_disass.h"
#include "xed-category-enum.h"
#include "xed_bb_chop.h"
#include <list>

//#define DEBUG
//#define VERBOSE


int qcomp(const void *a, const void *b) { return (((bb_t *)a)->addr)-(((bb_t *)b)->addr); }

std::list<bb_t> detect_static_basic_blocks(char* elf_data, unsigned int fsize) {
    // http://stackoverflow.com/questions/15352547/get-elf-sections-offsets
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;
    size_t file_length;

    char *strtab;
    int fd;
    int i = 0;

    bb_t* bbs = (bb_t*) calloc(sizeof(bb_t), fsize/4); 
    jump_t *jumps = (jump_t*) calloc(sizeof(jump_t), fsize/4);
    uint16_t *ilens = (uint16_t*) calloc(sizeof(uint16_t), fsize);

    uint64_t elf_section_bases[NUMBER_OF_SECTIONS];
    memset(elf_section_bases, 0, NUMBER_OF_SECTIONS*sizeof(uint64_t));
    uint64_t elf_section_sizes[NUMBER_OF_SECTIONS];
    memset(elf_section_sizes, 0, NUMBER_OF_SECTIONS*sizeof(uint64_t));
   
    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);
    strtab = elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;

#ifdef VERBOSE
    printf("\t%-25s %-16s %-s\n", "Name", "offset", "size");
#endif
    for (i=0; i<elf_hdr->e_shnum; i++) {
#ifdef VERBOSE 
        printf("\t%-25s 0x%-14lx %-ld\n",
            &strtab[elf_shdr[i].sh_name],
            elf_shdr[i].sh_offset,
            elf_shdr[i].sh_size);
#endif            
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".text")) {
            elf_section_bases[TEXT] = elf_shdr[i].sh_offset;
            elf_section_sizes[TEXT] = elf_shdr[i].sh_size;
        }
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".init")) {
            elf_section_bases[INIT] = elf_shdr[i].sh_offset;
            elf_section_sizes[INIT] = elf_shdr[i].sh_size;      
        }        
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".fini")) {
            elf_section_bases[FINI] = elf_shdr[i].sh_offset;        
            elf_section_sizes[FINI] = elf_shdr[i].sh_size;        
        }        
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".plt")) {
            elf_section_bases[PLT] = elf_shdr[i].sh_offset;        
            elf_section_sizes[PLT] = elf_shdr[i].sh_size;        
        }        
    }

    uint64_t jump_addr = 0;
    char cur_inst_len;
    int bb_count = 0, jumps_count = 0;

    xed_decoded_inst_t* xedd = (xed_decoded_inst_t*) malloc(sizeof(xed_decoded_inst_t));
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    xed_error_enum_t xed_error;
    
    xed_tables_init();

   // for(char section=0; section < NUMBER_OF_SECTIONS; ++section) {
    for(char section=TEXT; section < NUMBER_OF_SECTIONS; ++section) {
        uint64_t section_base = elf_section_bases[section],
            decode_window_start = section_base,
            section_len = elf_section_sizes[section];

        bbs[bb_count++].addr = decode_window_start; //start a BB at the entry point
        while(decode_window_start<section_base+section_len) {
          xed_decoded_inst_zero_set_mode(xedd, &dstate);
          xed_error = xed_decode(xedd, 
              XED_REINTERPRET_CAST(xed_uint8_t*,elf_data+decode_window_start),
              15+1);

          switch(xed_error) {
              case XED_ERROR_NONE:
                  cur_inst_len = xed_decoded_inst_get_length(xedd);
                  ilens[decode_window_start] = cur_inst_len;
                  if(terminates_bb(xedd)) {
                      jump_addr = xed_decoded_inst_get_branch_displacement(xedd) ?
                          xed_decoded_inst_get_branch_displacement(xedd) + decode_window_start + cur_inst_len :
                          0;
#ifdef DEBUG
                      if (xed_decoded_inst_get_branch_displacement(xedd) == 0) {
                       char* buffer = (char*) malloc(512);
                        xed_decoded_inst_dump(xedd, buffer, 512);
                        printf("%s\n", buffer);
                      }
                      printf("Bing! 0x%lx -> 0x%-lx (%d); next bb: 0x%lx\n", decode_window_start, jump_addr, xed_decoded_inst_get_branch_displacement(xedd), decode_window_start+cur_inst_len);
#endif
                      bbs[bb_count++].addr = decode_window_start + cur_inst_len; //start a new bb after the current jump instruction

                      if (jump_addr && jump_addr < 0x4000000000) {
                        bbs[bb_count++].addr = jump_addr; //start a new bb at the jump destination
                      }
                      jumps[jumps_count].addr = decode_window_start;
                      jumps[jumps_count].target = jump_addr;
                      jumps[jumps_count].isjump = 1;
                      jumps[jumps_count].conditional = (xed_decoded_inst_get_category(xedd) == XED_CATEGORY_COND_BR);
                      jumps[jumps_count].direct = (jump_addr > 0) || (xed_decoded_inst_get_category(xedd) == XED_CATEGORY_RET);
                      jumps_count++;
                  }
                  decode_window_start += ilens[decode_window_start];
                  break;

              case XED_ERROR_BUFFER_TOO_SHORT:
              case XED_ERROR_GENERAL_ERROR:
              default:
#ifdef DEBUG
                  printf("Decode error at %lx\n", decode_window_start);
#endif
                  decode_window_start += 1;
          } //switch 
        } //while
        bbs[bb_count-1].len = decode_window_start - (section_base+section_len);
    }
    // here we are done with the BB production

    //sort BBs and jumps according to their offset in the input file
    qsort(jumps, jumps_count, sizeof(jump_t), qcomp);
    qsort(bbs, bb_count, sizeof(bb_t), qcomp);
    
    // remove doubled BBs
    int k = 0, ctr = 0;
    for (k=0; k<bb_count; k++) {
      if(bbs[k].addr != bbs[ctr].addr) bbs[++ctr] = bbs[k];
    }
    int num_bbs = ctr;
    int num_jumps = jumps_count;


#ifdef DEBUG
    printf("\nGathered %d jumps\n", num_jumps);
    for(k=0; k<num_jumps; k++) printf("\t0x%x->0x%x\n", jumps[k].addr, jumps[k].target);
#endif

    int n = 0;
    k = 0, ctr = 0;
    while(jumps[ctr].addr < bbs[0].addr) ctr++;
    for (k=0; k<num_bbs+1; k++) {
      for (n=bbs[k].addr; n<bbs[k+1].addr; n++) {
          if(ilens[n] > 0) bbs[k].ilen++;
          bbs[k].len += ilens[n];
      }
      bbs[k].len = bbs[k+1].addr - bbs[k].addr;
      if(bbs[k+1].addr > jumps[ctr].addr) {
          bbs[k].jump.target = jumps[ctr].target;
          bbs[k].jump.isjump = jumps[ctr].isjump;
          bbs[k].jump.conditional = jumps[ctr].conditional;
          bbs[k].jump.direct = jumps[ctr].direct;
          for(int section=PLT; section < NUMBER_OF_SECTIONS; ++section) {
            if(bbs[k].addr >= elf_section_bases[section] && bbs[k].addr <= elf_section_bases[section]+elf_section_sizes[section]) {
                bbs[k].section = static_cast<ELF_SECTION>(section);
#ifdef DEBUG
                printf("Setting section of BB at %x to %d\n", bbs[k].addr, section);
#endif
                break;
            }
          }
          ctr++;
      }
    } //for

   // free(ilens);
   // free(jumps);
 //   *bbs_arr_ptr = realloc(*bbs_arr_ptr, num_bbs*sizeof(bb_t));
#ifdef DEBUG
    printf("\t%8s %7s %4s %4s %3s   %8s %3s %3s\n",
        "Address",
        "section",
        "len",
        "ilen",
        "BRA",
        "Target",
        "COND",
        "DIR");        
    for (k=0; k<num_bbs+1; k++) {
      printf("\t%8x %7d %4d %4d %3s ->%8x %3s %3s\n", 
          bbs[k].addr,
          bbs[k].section,
          bbs[k].len,
          bbs[k].ilen,
          bbs[k].jump.isjump ? "YES" : " NO", 
          bbs[k].jump.target,
          bbs[k].jump.conditional ? "YES" : " NO",
          bbs[k].jump.direct ? "YES" : " NO");
    }
#endif

#ifdef VERBOSE
    printf("\nGathered %d addresses and %d jumps\n", num_bbs, num_jumps);
#endif
    std::list<bb_t> ret;
    ret.insert(ret.begin(), bbs, bbs+(num_bbs+1));
    return ret;
}
