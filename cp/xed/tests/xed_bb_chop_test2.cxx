#include "xed_bb_chop.h"
#include <iostream>
#include <vector>

using namespace std;

#define VERBOSE

int main(int argc, char** argv) {
    if(argc != 3 && argc != 2) {
        printf("Usage: input_file [output_csv]\n");
        exit(1);
    }

    FILE* fp = fopen(argv[1], "r");
    size_t file_length;

    char *elf_data;
    size_t newLen = 0;

    if(fp != NULL) {
      fseek(fp, 0, SEEK_END);
      file_length = ftell(fp);
      elf_data = (char*)malloc(file_length+1);
      fseek(fp, 0, SEEK_SET);
      newLen = fread(elf_data, sizeof(char), file_length, fp);
      //printf("file length %zu, read %zu\n", file_length, newLen);

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

    std::vector<bbnowak_t> blocks = newer_detect_static_basic_blocks(elf_data, newLen);
    //cout << blocks.size() << endl;
    for(auto i: blocks)
        printf("0x%x,0x%x,%d\n", i.start, i.end, i.len);

    return 0;
}
