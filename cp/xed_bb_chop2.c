#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <unistd.h>
#include "xed_disass.h"
#include "include/xed-category-enum.h"

//#define DEBUG

int terminates_bb(xed_decoded_inst_t* inst) {
    xed_category_enum_t category = xed_decoded_inst_get_category(inst);
    return (category == XED_CATEGORY_CALL) ||
           (category == XED_CATEGORY_RET) ||
           (category == XED_CATEGORY_SYSCALL) ||
           (category == XED_CATEGORY_SYSRET) ||
           (category == XED_CATEGORY_SYSTEM) ||
           (category == XED_CATEGORY_UNCOND_BR) ||
           (category == XED_CATEGORY_COND_BR);

}

typedef struct {
  uint32_t addr;
  uint32_t target;
  uint16_t ilen;
  uint16_t len;
  char direct;
  char conditional;
  char isjump;
} bb_t;

int main(int argc, char** argv) {
    char* buf;
    size_t file_length;
    size_t idx;

    if(argc < 3) {
        printf("Need two arguments: input_file output_csv\n");
        exit(0);
    }
    
    // http://stackoverflow.com/questions/15352547/get-elf-sections-offsets
    FILE* fp = fopen(argv[1], "r");
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;
    void *elf_data;
    char *strtab;
    int fd;
    int i = 0, fsize = 0;
    uint64_t elf_plt_base = 0, elf_plt_size = 0, elf_text_base = 0, elf_text_size = 0;
    uint64_t elf_init_base = 0, elf_init_size = 0, elf_fini_base = 0, elf_fini_size = 0;
    
    fd = open(argv[1], O_RDONLY);
    fsize = lseek(fd, 0, SEEK_END);
    elf_data = mmap(NULL, fsize, PROT_READ, MAP_SHARED, fd, 0);
    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);
    strtab = (char *)elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;
    for (i=0; i<elf_hdr->e_shnum; i++) {
//#ifdef DEBUG
        printf("\t%-25s %-16p %-d\n",
            &strtab[elf_shdr[i].sh_name],
            elf_shdr[i].sh_offset,
            elf_shdr[i].sh_size);
//#endif            
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".text")) {
            elf_text_base = elf_shdr[i].sh_offset;
            elf_text_size = elf_shdr[i].sh_size;
        }
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".init")) {
            elf_init_base = elf_shdr[i].sh_offset;
            elf_init_size = elf_shdr[i].sh_size;        
        }        
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".fini")) {
            elf_fini_base = elf_shdr[i].sh_offset;
            elf_fini_size = elf_shdr[i].sh_size;        
        }        
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".plt")) {
            elf_plt_base = elf_shdr[i].sh_offset;
            elf_plt_size = elf_shdr[i].sh_size;        
        }        
    }
    close(fd);
    
    bb_t *bbs = calloc(sizeof(bb_t), fsize/4);
    bb_t *jumps = calloc(sizeof(bb_t), fsize/4);
    uint16_t *ilens = calloc(sizeof(uint16_t), fsize);
    
    if(fp != NULL) {
      fseek(fp, 0, SEEK_END);
      file_length = ftell(fp);
      buf = (char*)malloc(file_length+1);
      fseek(fp, 0, SEEK_SET);
      size_t newLen = fread(buf, sizeof(char), file_length, fp);
      printf("file length %zu, read %zu\n", file_length, newLen);
      if (newLen == 0) {
        fputs("Error reading file", stderr);
      } else {
        buf[newLen] = '\0';
      }
      fclose(fp);
    } else {
      printf("can't open file\n");
      return 1;
    }

    // TODO: need to disasm all AX sections, so text, plt, .init, .fini and anything else
//    uint64_t text_base = 0x2c00, start = text_base, stop = start + 1, text_len=0x1039c;
    uint64_t text_base = elf_text_base, start = text_base, stop = start + 1, text_len=elf_text_size;
    uint64_t jaddr = 0;
    i = start;
    int j = 0, m = 0;

    xed_decoded_inst_t* xedd = (xed_decoded_inst_t*) malloc(sizeof(xed_decoded_inst_t));
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    xed_error_enum_t xed_error;
    
    xed_tables_init();

    bbs[j++].addr = start;    
    while(start<text_base+text_len) {
      xed_decoded_inst_zero_set_mode(xedd, &dstate);
      xed_error = xed_decode(xedd, 
          XED_REINTERPRET_CAST(xed_uint8_t*,buf+start),
          15);

      switch(xed_error) {
          case XED_ERROR_NONE:
              ilens[start] = xed_decoded_inst_get_length(xedd);
              if(terminates_bb(xedd)) {
                  jaddr = xed_decoded_inst_get_branch_displacement(xedd) ?
                      xed_decoded_inst_get_branch_displacement(xedd) + start + ilens[start] :
                      0;
#ifdef DEBUG
                  printf("Bing! 0x%x -> 0x%x; next bb: 0x%x\n", start, jaddr, start+ilens[start]);
#endif
                  bbs[j++].addr = start+ilens[start];
                  if (jaddr && jaddr < 0x4000000000) bbs[j++].addr = jaddr;
                  jumps[m].addr = start;
                  jumps[m].target = jaddr;
                  jumps[m].isjump = 1;
                  jumps[m].conditional = (xed_decoded_inst_get_category(xedd) == XED_CATEGORY_COND_BR);
                  jumps[m].direct = (jaddr > 0) || (xed_decoded_inst_get_category(xedd) == XED_CATEGORY_RET);
                  m++;
              }
              start += ilens[start];
              break;

          case XED_ERROR_BUFFER_TOO_SHORT:
          case XED_ERROR_GENERAL_ERROR:
          default:
#ifdef DEBUG
              printf("Decode error at %x\n", start);
#endif
              start += 1;
      }        
    }

    int qcomp(const void *a, const void *b) { return (((bb_t *)a)->addr)-(((bb_t *)b)->addr); }
    qsort(bbs, j, sizeof(bb_t), qcomp);
    int k = 0, ctr = 0;
    for (k=0; k<j; k++) {
      if(bbs[k].addr != bbs[ctr].addr) bbs[++ctr] = bbs[k];
    }
    int num_bbs = ctr;
    int num_jumps = m;

    qsort(jumps, m, sizeof(bb_t), qcomp);
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
          bbs[k].target = jumps[ctr].target;
          bbs[k].isjump = jumps[ctr].isjump;
          bbs[k].conditional = jumps[ctr].conditional;
          bbs[k].direct = jumps[ctr].direct;
          ctr++;
      }
    }
    bbs[k-1].len = start - (text_base+text_len);

    printf("\nGathered %d addresses and %d jumps\n", num_bbs, num_jumps);

    FILE *f;
    f = fopen(argv[2], "w");
    fprintf(f,"addr;len;ilen;isbranch;target;conditional;direct\n");
    for(k=0; k<num_bbs+1; k++) fprintf(f,"%u;%u;%u;%u;%u;%u;%u\n",
          bbs[k].addr, 
          bbs[k].len,
          bbs[k].ilen,
          bbs[k].isjump ? 1 : 0, 
          bbs[k].target,
          bbs[k].conditional ? 1 : 0,
          bbs[k].direct ? 1 : 0);
    fclose(f);

#ifdef DEBUG
    printf("\t%18s %4s %4s %3s   %18s %3s %3s\n",
        "Address",
        "len",
        "ilen",
        "BRA",
        "Target",
        "CON",
        "DIR");        
    for (k=0; k<num_bbs+1; k++) {
      printf("\t%18p %4d %4d %3s ->%18x %3s %3s\n", 
          bbs[k].addr, 
          bbs[k].len,
          bbs[k].ilen,
          bbs[k].isjump ? "YES" : " NO", 
          bbs[k].target,
          bbs[k].conditional ? "YES" : " NO",
          bbs[k].direct ? "YES" : " NO");
    }
#endif
    return 0;
}
