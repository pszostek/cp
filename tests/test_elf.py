import unittest
import elf
#from xed import xed_iclass_enum_t2str, xed_decoded_inst_get_iclass

class TestELFFile(unittest.TestCase):
    def setUp(self):
        self.elf = elf.ELFFile("files/test_elf")

    def test_get_function_by_name(self):
        fun1_name = "Programmer::favoriteNumber()"
        fun1_mangled_name = "_ZN10Programmer14favoriteNumberEv"
        fun2_name = "Person::favoriteNumber()"
        undefined_function = "ThereIsNoSuchFunction"
        fun1_ = self.elf.get_function_by_name(fun1_name)
        fun1 = self.elf.get_function_by_mangled_name(fun1_mangled_name)
        self.assertEqual(fun1, fun1_)

        fun2 = self.elf.get_function_by_name(fun2_name)
        self.assertEqual(fun1.name, "Programmer::favoriteNumber()")
        self.assertEqual(fun1.mangled_name, "_ZN10Programmer14favoriteNumberEv")
        self.assertEqual(fun2.name, "Person::favoriteNumber()")
        self.assertEqual(fun2.mangled_name, "_ZN6Person14favoriteNumberEv")

        #now get unexisting symbol
        self.assertRaises(elf.ELFFileError, self.elf.get_function_by_name, undefined_function)

    def test_get_section_names(self):
        sections = [".dynsym", ".dynstr", ".rela.dyn", ".rela.plt", ".symtab", ".init"]
        section_names = self.elf.get_section_names()
        for section_name in sections:
            self.assertTrue(section_name in section_names)

    def test_get_symbol_text(self):
        import xed
        text = self.elf.get_symbol_text("main")
        inst_list = xed.disassemble_x64(text)
        self.assertEqual(len(inst_list), 66)

    def test_get_symbol_text2(self):
        import xed
        text = self.elf.get_symbol_text("main")

if __name__ == "__main__":
    unittest.main()
