import xed
import disass
from fun_list import get_text

text = get_text("/home/paszoste/cp/testG4Box")

inst_list = disass.disassemble_x64(text)

# il1 = inst_list[:5]
# il2 = inst_list[5:10]

for inst in inst_list:
    print inst
    print "unsigned imm:", inst.get_unsigned_immediate()
    print "signed imm:", inst.get_signed_immediate()
    print "number of operands:", inst.get_number_of_operands()
    for idx in xrange(0, inst.get_number_of_operands()):
        print inst.get_operand_length(idx)
    print "branch displacement: ", inst.get_branch_displacement()
    print "bytes:", disass.bytes_to_string(inst.get_bytes())
    print ""
    # if xed.terminates_bb(inst):
    #     print ">>",\
    #           inst.get_mnemonic_intel(),\
    #           xed.xed_operand_values_get_branch_displacement_int32(xed.xed_decoded_inst_operands_const(inst))
    # else:
    #     print inst.get_mnemonic_intel()

