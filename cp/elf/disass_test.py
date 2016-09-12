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

    def test_get_inst_list(self):
        """
        objdump output:
            4015ee:       44 3b ef                cmp    %edi,%r13d
            4015f1:       89 cf                   mov    %ecx,%edi
            4015f3:       45 0f 4f e3             cmovg  %r11d,%r12d
            4015f7:       45 8d 58 01             lea    0x1(%r8),%r11d
            4015fb:       41 0f af f8             imul   %r8d,%edi
            4015ff:       41 03 fe                add    %r14d,%edi
            401602:       44 3b ff                cmp    %edi,%r15d
            401605:       45 0f 4f c3             cmovg  %r11d,%r8d
            401609:       83 7c 24 70 00          cmpl   $0x0,0x70(%rsp)
            40160e:       75 0d                   jne    40161d <CalcSubSurface+0x11d>
        """
        df = self.hydro.get_inst_lists([(0x15ee, 0x160f)])
        self.assertEquals(len(df.index), 10)


if __name__ == "__main__":
    unittest.main()
