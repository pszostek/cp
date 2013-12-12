import xed
import disass
from fun_list import get_text

text = get_text("/home/paszoste/cp/tests/files/test_elf")

inst_list = xed.disassemble_x64(text)
for inst in inst_list:
    print inst, disass.bytes_to_string(inst.get_bytes())
    # if xed.terminates_bb(inst):
    #     print ">>",\
    #           inst.get_mnemonic_intel(),\
    #           xed.xed_operand_values_get_branch_displacement_int32(xed.xed_decoded_inst_operands_const(inst))
    # else:
    #     print inst.get_mnemonic_intel()

