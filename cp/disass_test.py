import disass
from fun_list import get_text

text = get_text("/home/paszoste/cp/cp/xed-ex1")

inst_list = disass.disassemble(1, text, len(text))
print inst_list
print inst_list.inst_count

i = inst_list[0]
print i._inst
print disass.xed_decoded_inst_get_operand_width(i)