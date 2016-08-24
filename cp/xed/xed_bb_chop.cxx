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

#define DEBUG
//#define VERBOSE

#ifdef DEBUG
    #define DBG(...) fprintf(stderr, __VA_ARGS__) 
#else
    #define DBG(msg)
#endif

#define LONGEST_POSSIBLE_INSTRUCTION 15

static int qcomp(const void *a, const void *b) { return (((bb_t *)a)->addr)-(((bb_t *)b)->addr); }

// this function checks if the elf file is the kernel
// it does so by checking for a .data..percpu section
static bool elffile_is_kernel(char *elf_data) {
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;
    char *strtab;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);
    strtab = elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;

    // iterate over sections
    for (unsigned i=0; i<elf_hdr->e_shnum; i++)
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".data..percpu")) return true;

    return false;
}

static int get_section_id_by_name(char *elf_data, const char *search_name) {
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;
    char *strtab;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);
    strtab = elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;

    // iterate over sections
    for (int i=0; i<elf_hdr->e_shnum; i++)
        if(!strcmp(&strtab[elf_shdr[i].sh_name], search_name)) return i;

    return -1;
}

static inline int32_t get_symtab_idx(char* elf_data) {
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);

    int32_t ret = -1;
    for (unsigned i=0; i<elf_hdr->e_shnum; i++) {
                 if(elf_shdr[i].sh_type == SHT_SYMTAB) {
                     ret = i;
                 }
    }

    // if there is no symtab, dig out dynsym at least; 
    // NB: the caller will not know if they're
    //     dealing with a SYMTAB or DYNSYM
    if (ret == -1) {
      DBG("There was no symtab found, looking for dynsym\n");
      for (unsigned i=0; i<elf_hdr->e_shnum; i++) {
                   if(elf_shdr[i].sh_type == SHT_DYNSYM) {
                       ret = i;
                   }
      }
    } else {
        DBG("Symtab found\n");
    }

    DBG("The search for symbols returned index %d\n", ret);
    return ret;
}

static inline uint32_t get_number_of_symbols(char* elf_data, int symtab_idx) {
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);

    // if kernel, read /tmp/vmlinux.symbols
    // ..beautifully hardcoded and broken in the future..
    if (elffile_is_kernel(elf_data)) {
        FILE *f = fopen("/tmp/vmlinux.symbols", "r");
        unsigned long long addr;
        unsigned char type;
        char name[1024];
        unsigned long long count = 0;

        while(fscanf(f, "%lx %c %s", &addr, &type, name) != EOF) {
            count++;
        }
        fclose(f);
        return count;
    }

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

static std::pair<uint64_t, uint64_t> get_strtab_info(char* elf_data) {
    // http://stackoverflow.com/questions/15352547/get-elf-sections-offsets
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;
    char *strtab;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);
    strtab = elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;

    for (unsigned i=0; i<elf_hdr->e_shnum; i++) {
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".strtab")) {
            return std::make_pair(elf_shdr[i].sh_offset, elf_shdr[i].sh_size);
        }
    }
    return std::make_pair(0L, 0L);
}


// Must be called after get_sections_info()
static void get_symbols_info(char* elf_data, 
        std::vector<unsigned long long>& elf_symbol_poff, 
        std::vector<unsigned long long>& elf_symbol_vaddr,         
        std::vector<unsigned long long>& elf_symbol_sizes,
        std::vector<unsigned long long>& elf_symbol_secids) {
    
    Elf64_Ehdr *elf_hdr = (Elf64_Ehdr *)elf_data;
    Elf64_Shdr *elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);

//    Elf64_Shdr *symtab = &elf_shdr[symtab_section_idx]; 

    DBG("Get Symbols Info called; pointers: elf_data@0x%lx, elf_symbol_poff@0x%lx, elf_symbol_sizes@0x%lx\n", elf_data, &elf_symbol_poff, &elf_symbol_sizes);
    DBG("This file is of type %d, (RELOC: %s)\n", elf_hdr->e_type, elf_hdr->e_type == ET_REL ? "True" : "False");

    uint64_t strtab_offset, strtab_size;
    std::tie(strtab_offset, strtab_size) = get_strtab_info(elf_data); // TODO: it won't work for the kernel
    char *strtab = elf_data + strtab_offset;

    uint32_t symtab_section_idx = get_symtab_idx(elf_data);
    // AN: remove crashes when symbols not found or return is -1? (not sure if this is right)
    // if it's the kernel, ignorei t and continue
    if ((symtab_section_idx == -1) && (!elffile_is_kernel(elf_data))) return;
    //printf("xx %lx %d\n", strtab, symtab_section_idx);
    
    uint32_t symtab_entries = get_number_of_symbols(elf_data, symtab_section_idx);

    DBG("There should be %d symbols\n", symtab_entries);
    DBG("%7s %-40s %-14s %-14s %-s\n", "Secn ID", "Symbol name", "offset", "last byte", "size (hex)");

    // this is an ugly patch but time gives us no choice. look only for "text" symbols
    // possibly some symbols will be forcibly assigned to the .text section which might cause problems

    if (elffile_is_kernel(elf_data)) {
        FILE *f = fopen("/tmp/vmlinux.symbols", "r");
        unsigned long long addr = 0, prev_addr = 0;
        unsigned char type;
        char name[1024];
        unsigned long long count = 0;
        unsigned long long local_vbase = 0;
        int text_section_id = get_section_id_by_name(elf_data, ".text");
        unsigned long long text_section_poff = elf_shdr[text_section_id].sh_offset;

        for(unsigned symidx = 0; symidx < symtab_entries; ++symidx) {
	    fscanf(f, "%lx %c %s", &addr, &type, name);
            // take the physical address of the first symbol as the base
	    if(symidx == 0) local_vbase = addr - text_section_poff;
//            elf_symbol_poff[symidx] = addr;
            elf_symbol_poff[symidx] = addr - local_vbase;
            elf_symbol_vaddr[symidx] = addr;
            elf_symbol_sizes[symidx] = 1;
            elf_symbol_secids[symidx] = 0xff;
        }
        fclose(f);
        
        // go in reverse to fill in sizes and fix aliasing 
        // (sizes are heuristically determined to be the distance to the next non-aliased symbol)
        for(signed symidx = symtab_entries - 2; symidx >= 0; symidx--) {
            // if aliased, inherit the size that's already been calculated
            if(elf_symbol_poff[symidx] == elf_symbol_poff[symidx+1]) {
                elf_symbol_sizes[symidx] = elf_symbol_sizes[symidx+1];
                continue;
            }
            // otherwise calculate distance
            elf_symbol_sizes[symidx] = elf_symbol_poff[symidx+1] - elf_symbol_poff[symidx];
        }
        
        #ifdef DEBUG
        for(unsigned symidx = 0; symidx < symtab_entries; ++symidx) {
            DBG("%7d %-30s %-14p %-14p %-ld (0x%-x) (VIRT: %p-%p)\n",
                elf_symbol_secids[symidx], // bogus
                NULL, // we don't know the names anymore
                elf_symbol_poff[symidx],
                elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] -1,
                elf_symbol_sizes[symidx],
                elf_symbol_sizes[symidx],
                elf_symbol_poff[symidx] + local_vbase,
                elf_symbol_poff[symidx] + local_vbase + elf_symbol_sizes[symidx] -1);
        }
        #endif
        return;
    }
    
    Elf64_Shdr *symtab = &elf_shdr[symtab_section_idx]; 
    Elf64_Sym *symtab_addr = (Elf64_Sym *)(elf_data + symtab->sh_offset);
    
    for(unsigned symidx = 0; symidx < symtab_entries; ++symidx) {
        Elf64_Sym *symbol = &(symtab_addr[symidx]);
        if(ELF64_ST_TYPE(symbol->st_info) != STT_FUNC) //omit non-function entries
            continue;
        if(symbol->st_shndx == SHN_UNDEF) {
            continue; //some weird stuff, e.g. free@@GLIBC_2.2.5
        } else if(symbol->st_shndx == SHN_ABS) { //e.g. file
            continue;
        } else {
            // Internally defined symbol
            if(symbol->st_size == 0) //omit 0-sized functions, e.g. call_gmon_start
                continue;
            elf_symbol_poff[symidx] = symbol->st_value - elf_shdr[symbol->st_shndx].sh_addr + elf_shdr[symbol->st_shndx].sh_offset;
            elf_symbol_vaddr[symidx] = symbol->st_value;
            elf_symbol_sizes[symidx] = symbol->st_size;
            elf_symbol_secids[symidx] = symbol->st_shndx;
            DBG("%7d %-30s %-14p %-14p %-ld (0x%-lx) (VIRT: %p-%p)\n",
                symbol->st_shndx,
                &strtab[symbol->st_name],
                elf_symbol_poff[symidx],
                elf_symbol_poff[symidx]+elf_symbol_sizes[symidx]-1,
                symbol->st_size,
                symbol->st_size,
                symbol->st_value,
                symbol->st_value+symbol->st_size-1);
        }
    }
}


static void get_sections_info(char* elf_data, 
    std::vector<unsigned long long>& elf_section_poff, 
    std::vector<unsigned long long>& elf_section_sizes,
    std::vector<unsigned long long>& elf_section_ids,
    std::vector<unsigned long long>& elf_section_vmas) {
    // http://stackoverflow.com/questions/15352547/get-elf-sections-offsets
    Elf64_Ehdr *elf_hdr;
    Elf64_Shdr *elf_shdr;
    char *strtab;

    elf_hdr = (Elf64_Ehdr *)elf_data;
    elf_shdr = (Elf64_Shdr *)(elf_data + elf_hdr->e_shoff);
    strtab = elf_data + elf_shdr[elf_hdr->e_shstrndx].sh_offset;

    DBG("\t%-4s %-25s %-10s %12s %-16s\n", "ID", "Section name", "offset in file", "size", "VMA");

    for (unsigned i=0; i<elf_hdr->e_shnum; i++) {
        DBG("\t[%2d] %-25s 0x%-10lx %12ld 0x%-16lx\n",
            i,
            &strtab[elf_shdr[i].sh_name],
            elf_shdr[i].sh_offset,
            elf_shdr[i].sh_size,
            elf_shdr[i].sh_addr);

        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".text")) {
            elf_section_poff[TEXT] = elf_shdr[i].sh_offset;
            elf_section_sizes[TEXT] = elf_shdr[i].sh_size;
            elf_section_ids[TEXT] = i;
            elf_section_vmas[TEXT] = elf_shdr[i].sh_addr;
        }
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".init")) {
            elf_section_poff[INIT] = elf_shdr[i].sh_offset;
            elf_section_sizes[INIT] = elf_shdr[i].sh_size;      
            elf_section_ids[INIT] = i;
            elf_section_vmas[INIT] = elf_shdr[i].sh_addr;
        }        
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".fini")) {
            elf_section_poff[FINI] = elf_shdr[i].sh_offset;
            elf_section_sizes[FINI] = elf_shdr[i].sh_size;        
            elf_section_ids[FINI] = i;
            elf_section_vmas[FINI] = elf_shdr[i].sh_addr;
        }        
        if(!strcmp(&strtab[elf_shdr[i].sh_name], ".plt")) {
            elf_section_poff[PLT] = elf_shdr[i].sh_offset;
            elf_section_sizes[PLT] = elf_shdr[i].sh_size;     
            elf_section_ids[PLT] = i;
            elf_section_vmas[PLT] = elf_shdr[i].sh_addr;
        }  
    }
}

// oops.
struct pair_hash {
    inline std::size_t operator()(const std::pair<unsigned long long, unsigned long long> &v) const {
        return v.first*31+v.second;
    }
};

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
    Elf64_Ehdr *elf_hdr = (Elf64_Ehdr *)elf_data;    
    
    std::unordered_set<unsigned long long> addrs; //this set will keep all the starting addresses of BB
    std::unordered_set<unsigned long long> end_addrs; //this set will keep all the presumed ending addresses of BB

    std::unordered_set<std::pair<unsigned long long, unsigned long long>, pair_hash> addrs_p; // need to store PH and VIRT addresses
    std::unordered_set<std::pair<unsigned long long, unsigned long long>, pair_hash> end_addrs_p; // as above but for BB end addresses

    std::vector<unsigned long long> elf_section_poff(NUMBER_OF_SECTIONS, 0);
    std::vector<unsigned long long> elf_section_sizes(NUMBER_OF_SECTIONS, 0);
    std::vector<unsigned long long> elf_section_ids(NUMBER_OF_SECTIONS, 0);
    std::vector<unsigned long long> elf_section_vmas(NUMBER_OF_SECTIONS, 0);

    get_sections_info(elf_data, elf_section_poff, elf_section_sizes, elf_section_ids, elf_section_vmas);

    // harvest addresses from ELF section boundaries
    for(unsigned secidx = INIT; secidx < FINI; ++secidx) {
        if(elf_section_sizes[secidx] > 0) {
//            if (elf_hdr->e_type != ET_REL) {
//            if (elf_hdr->e_type != ET_REL || true) {
                addrs.insert(elf_section_poff[secidx]);
                addrs_p.insert(std::make_pair(elf_section_poff[secidx], elf_section_poff[secidx] - elf_section_poff[secidx] + elf_section_vmas[secidx]));
                addrs.insert(elf_section_poff[secidx] + elf_section_sizes[secidx]);
                addrs_p.insert(std::make_pair(elf_section_poff[secidx] + elf_section_sizes[secidx], elf_section_poff[secidx] + elf_section_sizes[secidx] - elf_section_poff[secidx] + elf_section_vmas[secidx]));
                end_addrs.insert(elf_section_poff[secidx] + elf_section_sizes[secidx] - 1);
                end_addrs_p.insert(std::make_pair(elf_section_poff[secidx] + elf_section_sizes[secidx] - 1, elf_section_poff[secidx] + elf_section_sizes[secidx] - 1 - elf_section_poff[secidx] + elf_section_vmas[secidx]));

                DBG("[sec] S 0x%lx\n", elf_section_poff[secidx] + elf_section_sizes[secidx]);
                DBG("[sec] E 0x%lx\n", elf_section_poff[secidx] + elf_section_sizes[secidx] - 1);
                DBG("[sec] S PH %p VIRT %p\n", 
                    elf_section_poff[secidx] + elf_section_sizes[secidx], 
                    elf_section_poff[secidx] + elf_section_sizes[secidx] - elf_section_poff[secidx] + elf_section_vmas[secidx]);
                DBG("[sec] E PH %p VIRT %p\n", 
                    elf_section_poff[secidx] + elf_section_sizes[secidx] - 1,
                    elf_section_poff[secidx] + elf_section_sizes[secidx] - 1 - elf_section_poff[secidx] + elf_section_vmas[secidx]);

/*            } else {
                // TODO: remove, this won't be needed anymore
                addrs.insert(0);
                addrs.insert(elf_section_sizes[secidx]);
                end_addrs.insert(elf_section_sizes[secidx] - 1);
                #ifdef DEBUG
                printf("XXX DEL [sec] S 0x%lx [section in ET_REL]\n", elf_section_sizes[secidx]);
                printf("XXX DEL [sec] E 0x%lx [section in ET_REL]\n", elf_section_sizes[secidx] - 1);            
                #endif
                                                                                
            }*/
        }
    }

//    unsigned long long binary_base = get_binary_base(elf_data);
    int16_t symtab_idx = get_symtab_idx(elf_data);
    uint16_t number_of_symbols = get_number_of_symbols(elf_data, symtab_idx);
    std::vector<unsigned long long> elf_symbol_poff(number_of_symbols, 0UL);
    std::vector<unsigned long long> elf_symbol_vaddr(number_of_symbols, 0UL);
    std::vector<unsigned long long> elf_symbol_sizes(number_of_symbols, 0UL);
    std::vector<unsigned long long> elf_symbol_secids(number_of_symbols, 0xffffffff);

    get_symbols_info(elf_data, elf_symbol_poff, elf_symbol_vaddr, elf_symbol_sizes, elf_symbol_secids);

    // harvest addresses from ELF symbol boundaries
    for(unsigned symidx = 0; symidx < number_of_symbols; ++symidx) {
        if((elf_hdr->e_type == ET_REL) && (elf_symbol_secids[symidx] != elf_section_ids[TEXT]))
            continue;
        if(elf_symbol_sizes[symidx] > 0) {
//            addrs.insert(elf_symbol_poff[symidx] - binary_base);
            addrs.insert(elf_symbol_poff[symidx]);
            addrs_p.insert(std::make_pair(elf_symbol_poff[symidx], elf_symbol_vaddr[symidx]));            
//            addrs.insert(elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - binary_base);
//            end_addrs.insert(elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - binary_base - 1);
            addrs.insert(elf_symbol_poff[symidx] + elf_symbol_sizes[symidx]);
            addrs_p.insert(std::make_pair(elf_symbol_poff[symidx] + elf_symbol_sizes[symidx], elf_symbol_vaddr[symidx] + elf_symbol_sizes[symidx]));
            end_addrs.insert(elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - 1);
            end_addrs_p.insert(std::make_pair(elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - 1, elf_symbol_vaddr[symidx] + elf_symbol_sizes[symidx] - 1));
//            printf("[sym] S PH %p\n", elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - binary_base);     
//            printf("[sym] E PH %p\n", elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - binary_base - 1);            
            DBG("[sym] S PH %p VIRT %p\n", elf_symbol_poff[symidx], elf_symbol_vaddr[symidx]);
            DBG("[sym] S PH %p VIRT %p\n", elf_symbol_poff[symidx] + elf_symbol_sizes[symidx], elf_symbol_vaddr[symidx] + elf_symbol_sizes[symidx]);            
            DBG("[sym] E PH %p VIRT %p\n", elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - 1, elf_symbol_vaddr[symidx] + elf_symbol_sizes[symidx] - 1);            
//            if (elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - binary_base - 1 == 0x108c0) printf("POINT2: ins\n");
//            printf("sym end 0x%lx\n", elf_symbol_poff[symidx] + elf_symbol_sizes[symidx] - binary_base);
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
        unsigned long long section_poff = elf_section_poff[section];
        unsigned long long decode_window_start = section_poff;
        unsigned long long section_len = elf_section_sizes[section];
        unsigned long long section_vma = elf_section_vmas[section];
        
        // if it is a REL type, heuristically adjust addresses coming out, assuming the section base as 0
//        unsigned long long rel_adjustment = elf_hdr->e_type == ET_REL ? section_poff : 0;

        // the symbol/line physical offset + this adjustment = symbol/line VMA
//        unsigned long long global_adjustment = 0; // TODO
        
        DBG("Decoding section %p-%p (length: %d).\n", section_poff, section_poff + section_len - 1, section_len);
//        printf("The module %s of type REL, assuming rel_adjustment of -0x%lx bytes\n", 
//            elf_hdr->e_type == ET_REL ? "IS" : "is NOT",
//            rel_adjustment);
        
        while(decode_window_start < section_poff+section_len) { //decode the whole section
          xed_decoded_inst_zero_set_mode(xedd, &dstate);
          xed_error = xed_decode(xedd, 
              XED_REINTERPRET_CAST(xed_uint8_t*,elf_data+decode_window_start),
              LONGEST_POSSIBLE_INSTRUCTION+1);

          //since we are interested in a single instruction, we set the decoding window to the longest possible instruction (15 bytes)
          switch(xed_error) {
              case XED_ERROR_NONE:
                  cur_inst_len = xed_decoded_inst_get_length(xedd);
                  DBG("\tilen %d, terminates: %d\n", cur_inst_len, terminates_bb(xedd));
                  if(terminates_bb(xedd)) {
                      jump_target = xed_decoded_inst_get_branch_displacement(xedd) ?
//                          xed_decoded_inst_get_branch_displacement(xedd) + decode_window_start + cur_inst_len - rel_adjustment:
                          xed_decoded_inst_get_branch_displacement(xedd) + decode_window_start + cur_inst_len:
                          0;
                      #ifdef DEBUG
                      if (jump_target == 0) {
                       char* buffer = (char*) malloc(512);
                        xed_decoded_inst_dump(xedd, buffer, 512);
                        DBG("%s\n", buffer);
//                        printf("Zero branch displacement :( 0x%lx -> 0x%-lx (%d); next bb: 0x%lx\n", decode_window_start - rel_adjustment, jump_target, xed_decoded_inst_get_branch_displacement(xedd), decode_window_start+cur_inst_len-rel_adjustment);
                        DBG("Zero branch displacement :( 0x%lx -> 0x%-lx (%d); next bb: 0x%lx\n", decode_window_start, jump_target, xed_decoded_inst_get_branch_displacement(xedd), decode_window_start+cur_inst_len);
                      }
                      #endif

//                      addrs.insert(decode_window_start + cur_inst_len - rel_adjustment); //next bb after the current one
//                      end_addrs.insert(decode_window_start + cur_inst_len - rel_adjustment - 1); // last byte of the current instruction
                      addrs.insert(decode_window_start + cur_inst_len); //next bb after the current one
                      addrs_p.insert(std::make_pair(decode_window_start + cur_inst_len, decode_window_start + cur_inst_len - section_poff + section_vma));
                      end_addrs.insert(decode_window_start + cur_inst_len - 1); // last byte of the current instruction
                      end_addrs_p.insert(std::make_pair(decode_window_start + cur_inst_len - 1, decode_window_start + cur_inst_len - 1 - section_poff + section_vma));

//                      printf("[jmp] S 0x%lx\n", decode_window_start + cur_inst_len - rel_adjustment);
//                      printf("[jmp] E 0x%lx\n", decode_window_start + cur_inst_len - rel_adjustment - 1);
                      DBG("[jmp] S PH %p VIRT %p\n", decode_window_start + cur_inst_len, decode_window_start + cur_inst_len - section_poff + section_vma);
                      DBG("[jmp] E PH %p VIRT %p\n", decode_window_start + cur_inst_len - 1, decode_window_start + cur_inst_len - section_poff + section_vma - 1);

                      if (jump_target && jump_target < 0x4000000000) {
                          addrs.insert(jump_target);
                          addrs_p.insert(std::make_pair(jump_target, jump_target - section_poff + section_vma));
                          end_addrs.insert(jump_target - 1);
                          end_addrs_p.insert(std::make_pair(jump_target - 1, jump_target - 1 - section_poff + section_vma));

                          DBG("[tgt] S 0x%lx\n", jump_target);
                          DBG("[tgt] E 0x%lx\n", jump_target - 1);
                          DBG("[tgt] S PH %p VIRT %p\n", jump_target, jump_target - section_poff + section_vma);
                          DBG("[tgt] E PH %p VIRT %p\n", jump_target - 1, jump_target - 1 - section_poff + section_vma);                                                    
                      }
                  }
                  decode_window_start += cur_inst_len;
                  break;

              case XED_ERROR_BUFFER_TOO_SHORT:
              case XED_ERROR_GENERAL_ERROR: //decode window is too short - there is no meaningful instruction inside
              default:
                  DBG("Decode error at %lx\n", decode_window_start);
                  decode_window_start += 1;
          } //switch 
        } //while
    }

    DBG("BEGIN ADDRESS DUMP\n");
    std::vector<unsigned long long> ret(addrs.size());
    std::vector<std::pair<unsigned long long, unsigned long long>> ret_p(addrs_p.begin(), addrs_p.end());
    std::copy(addrs.begin(), addrs.end(), ret.begin());
//    std::copy(addrs_p.begin(), addrs_p.end(), ret_p.begin());
    sort(ret.begin(), ret.end());
    sort(ret_p.begin(), ret_p.end());

    std::vector<unsigned long long> end_ret(end_addrs.size());
    std::vector<std::pair<unsigned long long, unsigned long long>> end_ret_p(end_addrs_p.begin(), end_addrs_p.end());
    std::copy(end_addrs.begin(), end_addrs.end(), end_ret.begin());
//    std::copy(end_addrs_p.begin(), end_addrs_p.end(), end_ret_p.begin());
    sort(end_ret.begin(), end_ret.end());
    sort(end_ret_p.begin(), end_ret_p.end());

//    std::vector<bbnowak_t> ret_blocks(std::max(addrs.size(), end_addrs.size()));
    std::vector<bbnowak_t> ret_blocks;
//    printf("Captured %d start addresses, %d end addresses\n", ret.size(), end_ret.size());
    int i=0, j=0;
    int ret_s = ret.size(), end_ret_s = end_ret.size();
    int ret_p_s = ret_p.size(), end_ret_p_s = end_ret_p.size();
    unsigned long long sa = -1, ea = -1, sa_next = -1;
    unsigned long long sa_v = -1, ea_v = -1; // virtual correspondents
    // AN: todo: last block is chopped off, add boundary condition

    /*
    ea = end_ret[j];
    while(i < (ret_s-1)) {
      bbnowak_t *current_bb = new bbnowak_t;
      current_bb->start = 0; current_bb->end = 0; current_bb->len = 0;
      current_bb->vstart = 0; current_bb->vend = 0;
      sa = ret[i];
      sa_next = ret[i+1];
      current_bb->start = sa;
      while(ea < sa_next && j < end_ret_s) {
        current_bb->end = ea;
        current_bb->len = ea == 0 ? 0 : ea-sa+1;
        j++;
        ea = end_ret[j];
      };
      ret_blocks.push_back(*current_bb); // WHATEVER
      i++;
    }
    */

    ea = end_ret_p[j].first;
    while(i < (ret_p_s-1)) {
      bbnowak_t *current_bb = new bbnowak_t;
      current_bb->start = 0; current_bb->end = 0; current_bb->len = 0;
      current_bb->vstart = 0; current_bb->vend = 0;
      sa = ret_p[i].first;
      sa_v = ret_p[i].second;
      sa_next = ret_p[i+1].first;
      current_bb->start = sa;
      current_bb->vstart = sa_v;
      while(ea < sa_next && j < end_ret_p_s) {
        current_bb->end = ea;
        current_bb->vend = ea_v;
        current_bb->len = ea == 0 ? 0 : ea-sa+1;
        j++;
        ea = end_ret_p[j].first;
        ea_v = end_ret_p[j].second;
      };
      ret_blocks.push_back(*current_bb); // WHATEVER
      i++;
    }

/*    
    printf("BEGIN ADDRS ===================================\n");
    for (auto i: ret) {
        printf("0x%lx\n", i);
    }
    printf("END ADDRS ===================================\n");
    for (auto i: end_ret) {
        printf("0x%lx\n", i);
    }
*/
    return ret_blocks;
}
