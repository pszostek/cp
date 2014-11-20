#include "xed_bb_chop.h"

#define VERBOSE

int main(int argc, char** argv) {
    size_t idx;

    if(argc != 3 && argc != 2) {
        printf("Usage: input_file [output_csv]\n");
        exit(1);
    }

    FILE* fp = fopen(argv[1], "r");
    size_t file_length;

    char *elf_data;
    char *strtab;
    int fd;
    int i = 0, fsize = 0;
    size_t newLen = 0;

    if(fp != NULL) {
      fseek(fp, 0, SEEK_END);
      file_length = ftell(fp);
      elf_data = (char*)malloc(file_length+1);
      fseek(fp, 0, SEEK_SET);
      newLen = fread(elf_data, sizeof(char), file_length, fp);
      printf("file length %zu, read %zu\n", file_length, newLen);
      if (newLen == 0) {
        fputs("Error reading file", stderr);
        return 1;
      } else {
        elf_data[newLen] = '\0';
      }
      fclose(fp);
    } else {
      printf("can't open file\n");
      return 1;
    }

    std::list<bb_t> bbs = detect_basic_blocks(elf_data, newLen);
    printf("%lu\n", bbs.size());

    #ifdef VERBOSE
    printf("\t%8s %7s %4s %4s %3s   %8s %3s %3s\n",
        "Address",
        "section",
        "len",
        "ilen",
        "BRA",
        "Target",
        "COND",
        "DIR");        
    for (std::list<bb_t>::const_iterator k=bbs.begin(); k!=bbs.end(); ++k) {
      printf("\t%8x %7d %4d %4d %3s ->%8x %3s %3s\n", 
          k->addr,
          k->section,
          k->len,
          k->ilen,
          k->jump.isjump ? "YES" : " NO", 
          k->jump.target,
          k->jump.conditional ? "YES" : " NO",
          k->jump.direct ? "YES" : " NO");
    }
#endif
    return 0;
}