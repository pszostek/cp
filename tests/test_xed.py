import unittest
from elf.disass import disassemble_x64
from xed.xed import (xed_decoded_inst_t,
                 xed_decoded_inst_get_iclass,
                 xed_iclass_enum_t2str)
#xed.xed_iclass_enum_t2str(xed.xed_decoded_inst_get_iclass(inst))

class TestXED(unittest.TestCase):

    def setUp(self):
        self.main_text = open("files/test_elf.main.text", "rb").read()

    def test_inst_list_iter(self):
        inst_list = disassemble_x64(self.main_text)
        for inst in inst_list:
            self.assertTrue(isinstance(inst, xed_decoded_inst_t))

    def test_inst_list_selection_and_slice(self):
        inst_list = disassemble_x64(self.main_text)
        self.assertEqual(len(inst_list), 66)

        first_inst = inst_list[0]
        self.assertTrue(isinstance(first_inst, xed_decoded_inst_t))
        self.assertEqual(xed_iclass_enum_t2str(xed_decoded_inst_get_iclass(first_inst)), 'PUSH')

        last_inst = inst_list[-1]
        self.assertEqual(xed_iclass_enum_t2str(xed_decoded_inst_get_iclass(last_inst)), 'RET_NEAR')
        for idx, inst in enumerate(inst_list[:10]):
            self.assertEqual(inst.get_mnemonic_intel(), inst_list[idx].get_mnemonic_intel())

    def test_swig_extension(self):
        inst_list = disassemble_x64(self.main_text)
        inst = inst_list[2] # push rbx
        self.assertTrue(len(inst.get_mnemonic()) != 0)
        self.assertEqual(inst.get_mnemonic_intel(), 'push rbx')
        self.assertTrue(len(inst.get_mnemonic_att()) != 0)
        self.assertEqual(inst.get_number_of_operands(), 4)
        self.assertEqual(inst.get_iclass(), 'PUSH')
        self.assertEqual(inst.get_category(), "PUSH")

        inst = inst_list[3] # sub rsp, 0xb8
        self.assertTrue(len(inst.get_mnemonic()) != 0)
        self.assertEqual(inst.get_mnemonic_intel(), "sub rsp, 0xb8")
        self.assertTrue(len(inst.get_mnemonic_att()) != 0)
        self.assertEqual(inst.get_number_of_operands(), 3)
        self.assertEqual(inst.get_iclass(), 'SUB')
        self.assertEqual(inst.get_category(), "BINARY")
       # self.assertEqual(inst.get_category(), '')
        # il1 = inst_list[:5]
        # il2 = inst_list[5:10]
        # il1.extend(il2)
        # self.assertEqual(len(il1), 10)
       # il1.extend(il2)
       # self.assertEqual(len(il1), 15)

if __name__ == "__main__":
    unittest.main()
