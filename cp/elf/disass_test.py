import elffile
import unittest
import os

class TestDisass(unittest.TestCase):

    BIN_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../real_data")

    @classmethod
    def setUpClass(cls):
        cls.hydro = elffile.ELFFile(os.path.join(cls.BIN_PATH, 'hydro-pre'))

    def test_absolute_poff_in_asm_line(self):
        """
        objdump output:
            40173b:       e9 dd fe ff ff          jmpq   40161d <CalcSubSurface+0x11d>
        we expect the following asm line:
            jmpq 0x161d  # 0x173b - 0x11e = 0x161d
        an *incorrect* asm line would be:
            jmpq 0xfffffffffffffee2  # 0x0-0x11e
        """
        df = self.hydro.get_inst_lists([(0x173b, 0x173f)])
        asm_line = df.loc['CalcSubSurface', 0x173b, 0]['asm_line']
        self.assertIn('0x161d', asm_line)

    def test_absolute_poff_in_asm_line2(self):
        """
        objdump output:
            401434:       e8 e7 fd ff ff          callq  401220 <__libc_start_main@plt>
        incorrect asm:
            call 0xfffffffffffffdec
        correct asm:
            callq  0x1220

        observations:
            (uint64)0 - 0xfffffffffffffdec = 0x214
            0x1434-0x214 = '0x1220'
        """
        df = self.hydro.get_inst_lists([(0x1434, 0x1438)])
        asm_line = df.loc['_start', 0x1434, 0]['asm_line']
        self.assertIn('0x1220', asm_line)

if __name__ == "__main__":
    unittest.main()
