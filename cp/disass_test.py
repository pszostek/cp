import xed
from fun_list import get_text

text = get_text("/home/paszoste/cp/cp/xed-ex1")

inst_list = xed.disassemble(1, text, len(text))
for inst in inst_list:
    print inst
    print len(inst.get_bytes())
    # if xed.terminates_bb(inst):
    #     print ">>",\
    #           inst.get_mnemonic_intel(),\
    #           xed.xed_operand_values_get_branch_displacement_int32(xed.xed_decoded_inst_operands_const(inst))
    # else:
    #     print inst.get_mnemonic_intel()

