#include <algorithm>
#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <elf.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
//#include <unistd.h>
#include "xed_disass.h"
#include "xed-category-enum.h"
#include "xed_bb_chop.h"
#include <list>
#include <vector>
#include <unordered_map>
#include <unordered_set>

//#define DEBUG
//#define VERBOSE

#define LONGEST_POSSIBLE_INSTRUCTION 15

static int qcomp(const void *a, const void *b) { return (((bb_t *)a)->addr)-(((bb_t *)b)->addr); }

static inline int32_t get_symtab_idx(char* elf_data) {
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);

#ifdef VERBOSE
    printf("\t%-25s %-16s %-s\n", "Symbol name", "offset", "size");
#endif
    int32_t ret = -1;
    for (unsigned i=0; i<elf_hdr->e_shnum; i++) {
                 if(elf_shdr[i].sh_type == SHT_SYMTAB) {
                     ret = i;
                 }
    }
    return ret;
}
static inline uint32_t get_number_of_symbols(char* elf_data, int symtab_idx) {
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);

    if(elf_shdr[symtab_idx].sh_entsize == 0) // in some cases sh_entsize is 0, e.g. for the linux kernel
        return 0;
    else
        return elf_shdr[symtab_idx].sh_size / elf_shdr[symtab_idx].sh_entsize;
}

static inline Elf64_Shdr *elf_sheader(Elf64_Ehdr *hdr) {
        return (Elf64_Shdr *)(hdr + hdr->e_shoff);
}
 
static inline Elf64_Shdr *elf_section(Elf64_Ehdr *hdr, int idx) {
        return &elf_sheader(hdr)[idx];
}

static unsigned long long get_binary_base(char* elf_data) {
        /*
        def _get_binary_base(self):
            for segment in self.iter_segments():
                if segment['p_type'] == "PT_LOAD" and segment['p_offset'] == 0:
                     return segment['p_vaddr']
            raise ELFFileError("Can't find base for the .text segment")
            */
    Elf64_Ehdr *elf_hdr = (Elf64_Ehdr *)elf_data;
    Elf64_Phdr *p_hdr = (Elf64_Phdr *)(elf_data + elf_hdr->e_phoff);
    unsigned long long ret = 0UL;
    for(unsigned ph_idx = 0; ph_idx < elf_hdr->e_phnum; ++ph_idx) {
        if(p_hdr[ph_idx].p_type == PT_LOAD && p_hdr[ph_idx].p_offset == 0) {
            ret = p_hdr[ph_idx].p_vaddr;
            break;
        }
    }
    return ret; 

}

static void get_symbols_info(char* elf_data, std::vector<unsigned long long>& elf_symbol_bases, std::vector<unsigned long long>& elf_symbol_sizes) {
    #ifdef DEBUG
    printf("Get Symbols Info called: elf_data@0x%x, elf_symbol_bases@0x%x, elf_symbol_sizes@0x%x\n", elf_data, elf_symbol_bases, elf_symbol_sizes);
    #endif
    
    Elf64_Ehdr *elf_hdr = (Elf64_Ehdr *)elf_data;
    Elf64_Shdr *elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);

    char *strtab = elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;

    uint32_t symtab_section_idx = get_symtab_idx(elf_data);
    // AN: remove crashes when symbols not found or return is -1? (not sure if this is right)
    if (symtab_section_idx == -1) return;
    //printf("xx %x %d\n", strtab, symtab_section_idx);
    
    uint32_t symtab_entries = get_number_of_symbols(elf_data, symtab_section_idx);

    Elf64_Shdr *symtab = &elf_shdr[symtab_section_idx]; 
    Elf64_Sym *symtab_addr = (Elf64_Sym *)(elf_data + symtab->sh_offset);
    
    #ifdef DEBUG
    printf("\t%-25s %-16s %-s\n", "Symbol name", "offset", "size");
    #endif

    for(unsigned symidx = 0; symidx < symtab_entries; ++symidx) {
        Elf64_Sym *symbol = &(symtab_addr[symidx]);
        if(ELF64_ST_TYPE(symbol->st_info) != STT_FUNC) //omit non-function entries
            continue;
        if(symbol->st_shndx == SHN_UNDEF) {
            continue; //some weird stuff, e.g. free@@GLIBC_2.2.5

            // External symbol, lookup value
//            Elf64_Shdr *strtab = elf_section(hdr, symtab->sh_link);
//            const char *name = (const char *)hdr + strtab->sh_offset + symbol->st_name;

//            extern void *elf_lookup_symbol(const char *name);
//            void *target = elf_lookup_symbol(name);
//
//            if(target == NULL) {
//                // Extern symbol not found
//                if(ELF64_ST_BIND(symbol->st_info) & STB_WEAK) {
//                    // Weak symbol initialized as 0
//                    return 0;
//                } else {
//                    fprintf(stderr, "Undefined External Symbol : %s.\n", name);
//                    return 1;
       //
       //     } else {
       //         return (int)target;

        //    }
        } else if(symbol->st_shndx == SHN_ABS) { //e.g. file
            continue;
        } else {
            // Internally defined symbol
            if(symbol->st_size == 0) //omit 0-sized functions, e.g. call_gmon_start
                continue;
            elf_symbol_bases[symidx] = symbol->st_value;;
            elf_symbol_sizes[symidx] = symbol->st_size;
#ifdef DEBUG
            // AN: todo: this crashes on /lib64/libdl*so, presumably there is something missing
                printf("\t%d %-25s 0x%-14lx %-ld\n",
                symbol->st_name,
                &strtab[symbol->st_name],
                symbol->st_value,
                symbol->st_size);
#endif
        }
    }
}

static void get_sections_info(char* elf_data, std::vector<unsigned long long>& elf_section_bases, std::vector<unsigned long long>& elf_section_sizes) {
    // http://stackoverflow.com/questions/15352547/get-elf-sections-offsets
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;
    char *strtab;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);
    strtab = elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;

#ifdef DEBUG
    printf("\t%-25s %-16s %-s\n", "Section name", "offset", "size");
#endif

    for (unsigned i=0; i<elf_hdr->e_shnum; i++) {
#ifdef DEBUG
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
}


/* This function attempts to track BB boundaries according to the blessed Levinthal's method.
 * It keeps a set of starting addresses coming from various logical sources:
 *    * symbol offsets
 *    ? symbol offsets + symbol sizes + 1
 *    * section offsets
 *    ? section offsets + section sizes + 1
 *    * addresses of jump instructions + len(jump instuction)
 *    * destination addresses of jump instructions
 *  It also attempts to track BB end addresses (=the address of the last byte) from the following sources:
 *    * last byte of an ELF section
 *    * last byte of a symbol
 *    * addresses of jump instructions + len(jump instructio) - 1
 *    * destination addreses of jump instrictions - 1
 *  Ways to detect screwups:
 *    - look for 0 sized blocks (,0$)
 *    - look for very long blocks (visually)
 *    - look for blocks where either address is 0 (0x0,)
 */

std::vector<bbnowak_t> newer_detect_static_basic_blocks(char* elf_data, unsigned int fsize) {
    std::unordered_set<unsigned long long> addrs; //this set will keep all the starting addresses of BB
    std::unordered_set<unsigned long long> end_addrs; //this set will keep all the presumed ending addresses of BB

    std::vector<unsigned long long> elf_section_bases(NUMBER_OF_SECTIONS, 0);
    std::vector<unsigned long long> elf_section_sizes(NUMBER_OF_SECTIONS, 0);

    get_sections_info(elf_data, elf_section_bases, elf_section_sizes);

    // harvest addresses from ELF section boundaries
    for(unsigned secidx = INIT; secidx < FINI; ++secidx) {
        if(elf_section_sizes[secidx] > 0) {
            addrs.insert(elf_section_bases[secidx]);
            addrs.insert(elf_section_bases[secidx] + elf_section_sizes[secidx] );
            end_addrs.insert(elf_section_bases[secidx] + elf_section_sizes[secidx] - 1);        
            #ifdef DEBUG
            //printf("sec start 0x%x", elf_section_bases[secidx]);
            printf("[sec] S 0x%x\n", elf_section_bases[secidx] + elf_section_sizes[secidx]);
            printf("[sec] E 0x%x\n", elf_section_bases[secidx] + elf_section_sizes[secidx] - 1);            
            //if (elf_section_bases[secidx] + elf_section_sizes[secidx] - 1 == 0x108c0) printf("POINT1: ins\n");
            // printf("sec end 0x%x", elf_section_bases[secidx] + elf_section_sizes[secidx]);
            #endif
        }
    }

    unsigned long long binary_base = get_binary_base(elf_data);
    int16_t symtab_idx = get_symtab_idx(elf_data);
    uint16_t number_of_symbols = get_number_of_symbols(elf_data, symtab_idx);
    std::vector<unsigned long long> elf_symbol_bases(number_of_symbols, 0UL);
    std::vector<unsigned long long> elf_symbol_sizes(number_of_symbols, 0UL);

    get_symbols_info(elf_data, elf_symbol_bases, elf_symbol_sizes);

    // harvest addresses from ELF symbol boundaries
    for(unsigned symidx = 0; symidx < number_of_symbols; ++symidx) {
        if(elf_symbol_sizes[symidx] > 0) {
            addrs.insert(elf_symbol_bases[symidx] - binary_base);
#ifdef DEBUG
//            printf("sym start 0x%x\n", elf_symbol_bases[symidx] - binary_base);
#endif
            addrs.insert(elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base);
            end_addrs.insert(elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base - 1);
#ifdef DEBUG
            printf("[sym] S 0x%x\n", elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base);     
            printf("[sym] E 0x%x\n", elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base - 1);            
            if (elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base - 1 == 0x108c0) printf("POINT2: ins\n");
//            printf("sym end 0x%x\n", elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base);
#endif
        }
    }

    unsigned long long jump_target = 0;
    char cur_inst_len;

    xed_decoded_inst_t* xedd = (xed_decoded_inst_t*) malloc(sizeof(xed_decoded_inst_t));
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    xed_error_enum_t xed_error;
    
    xed_tables_init();

    for(char section=0; section < NUMBER_OF_SECTIONS; ++section) {
        unsigned long long section_base = elf_section_bases[section];
        unsigned long long decode_window_start = section_base;
        unsigned long long section_len = elf_section_sizes[section];
        
        while(decode_window_start < section_base+section_len) { //decode the whole section
          xed_decoded_inst_zero_set_mode(xedd, &dstate);
          xed_error = xed_decode(xedd, 
              XED_REINTERPRET_CAST(xed_uint8_t*,elf_data+decode_window_start),
              LONGEST_POSSIBLE_INSTRUCTION+1);
          //since we are interested in a single instruction, we set the decoding window to the longest possible instruction (15 bytes)

          switch(xed_error) {
              case XED_ERROR_NONE:
                  cur_inst_len = xed_decoded_inst_get_length(xedd);
                  if(terminates_bb(xedd)) {
                      jump_target = xed_decoded_inst_get_branch_displacement(xedd) ?
                          xed_decoded_inst_get_branch_displacement(xedd) + decode_window_start + cur_inst_len :
                          0;
#ifdef DEBUG
                      if (jump_target == 0) {
                       char* buffer = (char*) malloc(512);
                        xed_decoded_inst_dump(xedd, buffer, 512);
                        printf("%s\n", buffer);
                        printf("Zero branch displacement :( 0x%lx -> 0x%-lx (%d); next bb: 0x%lx\n", decode_window_start, jump_target, xed_decoded_inst_get_branch_displacement(xedd), decode_window_start+cur_inst_len);
                      }
#endif
                      addrs.insert(decode_window_start + cur_inst_len); //next bb after the current one
                      end_addrs.insert(decode_window_start + cur_inst_len - 1); // last byte of the current instruction

                      #ifdef DEBUG
                      printf("[jmp] S 0x%x\n", decode_window_start + cur_inst_len);
                      printf("[jmp] E 0x%x\n", decode_window_start + cur_inst_len - 1);
                      if(decode_window_start + cur_inst_len - 1 == 0x108c0) printf("POINT3: ins\n");
                      #endif

                      if (jump_target && jump_target < 0x4000000000) {
                          addrs.insert(jump_target);
                          end_addrs.insert(jump_target - 1);
                          #ifdef DEBUG
                          printf("[tgt] S 0x%x\n", jump_target);
                          printf("[tgt] E 0x%x\n", jump_target - 1);
                          if(jump_target - 1 == 0x108c0) printf("POINT4: ins, 0x%x\n", jump_target); 
                          #endif
                      }
                  }
                  decode_window_start += cur_inst_len;
                  break;

              case XED_ERROR_BUFFER_TOO_SHORT:
              case XED_ERROR_GENERAL_ERROR: //decode window is too short - there is no meaningful instruction inside
              default:
#ifdef DEBUG
                  printf("Decode error at %lx\n", decode_window_start);
#endif
                  decode_window_start += 1;
          } //switch 
        } //while
    }

    #ifdef DEBUG
    printf("BEGIN ADDRESS DUMP\n");
    #endif
    std::vector<unsigned long> ret(addrs.size());    
    std::copy(addrs.begin(), addrs.end(), ret.begin());
    sort(ret.begin(), ret.end());

    std::vector<unsigned long> end_ret(end_addrs.size());    
    std::copy(end_addrs.begin(), end_addrs.end(), end_ret.begin());
    sort(end_ret.begin(), end_ret.end());

//    std::vector<bbnowak_t> ret_blocks(std::max(addrs.size(), end_addrs.size()));
    std::vector<bbnowak_t> ret_blocks;
//    printf("Captured %d start addresses, %d end addresses\n", ret.size(), end_ret.size());
    int i=0, j=0, ret_s = ret.size(), end_ret_s = end_ret.size();
    unsigned long long sa = -1, ea = -1, sa_next = -1;
    // AN: todo: last block is chopped off, add boundary condition
    ea = end_ret[j];
    while(i < (ret_s-1)) {
      bbnowak_t *current_bb = new bbnowak_t;
      current_bb->start = 0; current_bb->end = 0; current_bb->len = 0;
      sa = ret[i];
      sa_next = ret[i+1];
//      printf("\n0x%x,", sa);
      current_bb->start = sa;
      while(ea < sa_next && j < end_ret_s) {
//        printf("0x%x,%d,", ea, ea-sa);
        current_bb->end = ea;
        current_bb->len = ea == 0 ? 0 : ea-sa+1;
        j++;
        ea = end_ret[j];
      };
      ret_blocks.push_back(*current_bb); // WHATEVER
      i++;
    }
//    printf("\n\n");

/*    
    printf("BEGIN ADDRS ===================================\n");
    for (auto i: ret) {
        printf("0x%x\n", i);
    }
    printf("END ADDRS ===================================\n");
    for (auto i: end_ret) {
        printf("0x%x\n", i);
    }
*/
    return ret_blocks;
}


/* This functions tries to detect BB boundaries according to the blessed Levinthal's method.
 * It keeps a set of starting addresses coming from various logical sources:
 *    * symbol offsets
 *    * symbol offsets + symbol sizes + 1
 *    * section offsets
 *    * section offsets + section sizes + 1
 *    * addresses of jump instructions + len(jump instuction)
 *    * destination addresses of jump instructions
 */

std::vector<unsigned long> new_detect_static_basic_blocks(char* elf_data, unsigned int fsize) {
    std::unordered_set<unsigned long long> addrs; //this set will keep all the starting addresses of BB

    std::vector<unsigned long long> elf_section_bases(NUMBER_OF_SECTIONS, 0);
    std::vector<unsigned long long> elf_section_sizes(NUMBER_OF_SECTIONS, 0);

    get_sections_info(elf_data, elf_section_bases, elf_section_sizes);

    for(unsigned secidx = INIT; secidx < FINI; ++secidx) {
        addrs.insert(elf_section_bases[secidx]);
#ifdef DEBUG
        printf("sec start 0x%x", elf_section_bases[secidx]);
#endif
        addrs.insert(elf_section_bases[secidx] + elf_section_sizes[secidx] );
#ifdef DEBUG
        printf("sec end 0x%x", elf_section_bases[secidx] + elf_section_sizes[secidx]);
#endif
    }
    unsigned long long binary_base = get_binary_base(elf_data);

    int16_t symtab_idx = get_symtab_idx(elf_data);
    uint16_t number_of_symbols = get_number_of_symbols(elf_data, symtab_idx);
    std::vector<unsigned long long> elf_symbol_bases(number_of_symbols, 0UL);
    std::vector<unsigned long long> elf_symbol_sizes(number_of_symbols, 0UL);

    get_symbols_info(elf_data, elf_symbol_bases, elf_symbol_sizes);

    for(unsigned symidx = 0; symidx < number_of_symbols; ++symidx) {
        if(elf_symbol_sizes[symidx] > 0) {
            addrs.insert(elf_symbol_bases[symidx] - binary_base);
#ifdef DEBUG
            printf("sym start 0x%x\n", elf_symbol_bases[symidx] - binary_base);
#endif
            addrs.insert(elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base);
#ifdef DEBUG
            printf("sym end 0x%x\n", elf_symbol_bases[symidx] + elf_symbol_sizes[symidx] - binary_base);
#endif
        }
    }

    unsigned long long jump_addr = 0;
    char cur_inst_len;

    xed_decoded_inst_t* xedd = (xed_decoded_inst_t*) malloc(sizeof(xed_decoded_inst_t));
    xed_state_t dstate;
    xed_state_zero(&dstate);
    xed_state_init(&dstate,
        XED_MACHINE_MODE_LONG_64,
        XED_ADDRESS_WIDTH_64b,
        XED_ADDRESS_WIDTH_64b);
    xed_error_enum_t xed_error;
    
    xed_tables_init();

    for(char section=0; section < NUMBER_OF_SECTIONS; ++section) {
        unsigned long long section_base = elf_section_bases[section];
        unsigned long long decode_window_start = section_base;
        unsigned long long section_len = elf_section_sizes[section];
        
        while(decode_window_start < section_base+section_len) { //decode the whole section
          xed_decoded_inst_zero_set_mode(xedd, &dstate);
          xed_error = xed_decode(xedd, 
              XED_REINTERPRET_CAST(xed_uint8_t*,elf_data+decode_window_start),
              LONGEST_POSSIBLE_INSTRUCTION+1);
          //since we are interested in a single instruction, we set the decoding window to the longest possible instruction (15 bytes)

          switch(xed_error) {
              case XED_ERROR_NONE:
                  cur_inst_len = xed_decoded_inst_get_length(xedd);
                  if(terminates_bb(xedd)) {
                      jump_addr = xed_decoded_inst_get_branch_displacement(xedd) ?
                          xed_decoded_inst_get_branch_displacement(xedd) + decode_window_start + cur_inst_len :
                          0;
#ifdef DEBUG
                      if (jump_addr == 0) {
                       char* buffer = (char*) malloc(512);
                        xed_decoded_inst_dump(xedd, buffer, 512);
                        printf("%s\n", buffer);
                      }
                      printf("Zero branch displacement :( 0x%lx -> 0x%-lx (%d); next bb: 0x%lx\n", decode_window_start, jump_addr, xed_decoded_inst_get_branch_displacement(xedd), decode_window_start+cur_inst_len);
#endif
                      addrs.insert(decode_window_start + cur_inst_len); //next bb after the current one

                      if (jump_addr && jump_addr < 0x4000000000) {
                          addrs.insert(jump_addr);
                      }
                  }
                  decode_window_start += cur_inst_len;
                  break;

              case XED_ERROR_BUFFER_TOO_SHORT:
              case XED_ERROR_GENERAL_ERROR: //decode window is too short - there is no meaningful instruction inside
              default:
#ifdef DEBUG
                  printf("Decode error at %lx\n", decode_window_start);
#endif
                  decode_window_start += 1;
          } //switch 
        } //while
    }
    std::vector<unsigned long> ret(addrs.size());
    std::copy(addrs.begin(), addrs.end(), ret.begin());
    sort(ret.begin(), ret.end());
    return ret;
}

std::vector<int> test() {
    return std::vector<int>(10,0);
}
std::vector<bb_t> detect_static_basic_blocks(char* elf_data, unsigned int fsize) {
    size_t file_length;

    bb_t* bbs = (bb_t*) calloc(sizeof(bb_t), fsize/4); 
    std::unordered_map<unsigned long long, bb_t> bbs_map; 
    jump_t *jumps = (jump_t*) calloc(sizeof(jump_t), fsize/4);
    //uint16_t *ilens = (uint16_t*) calloc(sizeof(uint16_t), fsize);
    std::unordered_map<unsigned long long, uint16_t> ilens;
    //map<unsigned long long, uint16_t> ilens;

    std::vector<unsigned long long> elf_section_bases(NUMBER_OF_SECTIONS, 0);
    std::vector<unsigned long long> elf_section_sizes(NUMBER_OF_SECTIONS, 0);

    get_sections_info(elf_data, elf_section_bases, elf_section_sizes);

    unsigned long long jump_addr = 0;
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
        unsigned long long section_base = elf_section_bases[section],
            decode_window_start = section_base,
            section_len = elf_section_sizes[section];

        bb_t cur_bb;
        cur_bb.addr = decode_window_start;
        bbs_map[decode_window_start] = cur_bb; //start a BB at the entry point
        while(decode_window_start < section_base+section_len) { //decode the whole section
          xed_decoded_inst_zero_set_mode(xedd, &dstate);
          xed_error = xed_decode(xedd, 
              XED_REINTERPRET_CAST(xed_uint8_t*,elf_data+decode_window_start),
              LONGEST_POSSIBLE_INSTRUCTION+1);
          //since we are interested in a single instruction, we set the decoding window to the longest possible instruction (15 bytes)

          switch(xed_error) {
              case XED_ERROR_NONE:
                  cur_inst_len = xed_decoded_inst_get_length(xedd);
                  ilens[decode_window_start] = cur_inst_len;
                  if(terminates_bb(xedd)) {
                      jump_addr = xed_decoded_inst_get_branch_displacement(xedd) ?
                          xed_decoded_inst_get_branch_displacement(xedd) + decode_window_start + cur_inst_len :
                          0;
#ifdef DEBUG
                      if (jump_addr == 0) {
                       char* buffer = (char*) malloc(512);
                        xed_decoded_inst_dump(xedd, buffer, 512);
                        printf("%s\n", buffer);
                      }
                      printf("Zero branch displacement :( 0x%lx -> 0x%-lx (%d); next bb: 0x%lx\n", decode_window_start, jump_addr, xed_decoded_inst_get_branch_displacement(xedd), decode_window_start+cur_inst_len);
#endif
                      bb_t next_bb;
                      next_bb.addr = decode_window_start + cur_inst_len;
                      bbs_map[decode_window_start + cur_inst_len] = next_bb; //start a new bb after the current jump instruction

                      if (jump_addr && jump_addr < 0x4000000000) {
                          if(bbs_map.find(jump_addr) == bbs_map.end()) {
                            bb_t dest_bb;
                            dest_bb.addr = jump_addr;
                              bbs_map[jump_addr] = dest_bb; //start a new bb at the jump destination
                          }
                      }
                      if(jump_addr) { //add a new jump only when we know the destination address
                        jump_t cur_jump;
                        cur_jump.addr = decode_window_start;
                        cur_jump.target = jump_addr;
                        cur_jump.isjump = 1;
                        cur_jump.conditional = (xed_decoded_inst_get_category(xedd) == XED_CATEGORY_COND_BR);
                        cur_jump.direct = (jump_addr > 0) || (xed_decoded_inst_get_category(xedd) == XED_CATEGORY_RET);
                        jumps[jumps_count++] = cur_jump;
                      }
                  }
                  decode_window_start += cur_inst_len;
                  break;

              case XED_ERROR_BUFFER_TOO_SHORT:
              case XED_ERROR_GENERAL_ERROR: //decode window is too short - there is no meaningful instruction inside
              default:
#ifdef DEBUG
                  printf("Decode error at %lx\n", decode_window_start);
#endif
                  decode_window_start += 1;
          } //switch 
        } //while
        bbs[bb_count-1].len = decode_window_start - (section_base+section_len); //we processed .text - set length of the last BB
    }
    // here we are done with the BB production

    //sort BBs and jumps according to their offset in the input file
    qsort(jumps, jumps_count, sizeof(jump_t), qcomp);
    qsort(bbs, bb_count, sizeof(bb_t), qcomp);
    
    // remove doubled BBs
    // TODO: Pawel: where the doubled BBs come from?
    int k = 0, ctr = 0;
    for (k=0; k<bb_count; k++) {
      if(bbs[k].addr != bbs[ctr].addr) bbs[++ctr] = bbs[k];
    }
    int num_bbs = ctr;

#ifdef DEBUG
    printf("\nGathered %d jumps\n", jumps_count);
    for(k=0; k<jumps_count; k++) printf("\t0x%x->0x%x\n", jumps[k].addr, jumps[k].target);
#endif

    int n = 0;
    k = 0, ctr = 0;
    while(jumps[ctr].addr < bbs[0].addr) ctr++;
    for (k=0; k <= num_bbs; k++) {
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
    std::vector<bb_t> ret;
    ret.insert(ret.begin(), bbs, bbs+(num_bbs+1));
    return ret;
}
