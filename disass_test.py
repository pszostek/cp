import cp
import cp.elf as elf
import cp.elf.disass as disass
import cp.xed.xed as xed

if __name__ == "__main__":
    binary = elf.ELFFile("./real_data/hydro")
    input_dict = {"./real_data/hydro": [(0x1500, 0x1510), (0x1510, 0x1520), (0x1520, 0x1540)]}
    df = disass.get_inst_lists_for_basic_blocks(input_dict)
    print(df)

