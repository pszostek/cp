from xed import xed
from elf import disass
from elf import elffile as elf
import unittest

class TestDisass(unittest.TestCase):
    def setUp(self):
        self.elf = elf.ELFFile("files/test_elf")
    
    def test_get_basic_block(self):
        bb = disass.get_basic_block(self.elf, 0x81c)
        self.assertTrue(isinstance(bb, xed.inst_list_t))
        self.assertTrue(len(bb) > 0 )
        self.assertTrue(xed.terminates_bb(bb[-1]))

    def test_get_basic_blocks(self):
        bbs = disass.get_basic_blocks(self.elf, [0x964, 0x97a, 0x992, 0x7f4])
        for bb in bbs:
            self.assertTrue(xed.terminates_bb(bb[-1]))
            self.assertTrue(len(bb) > 0)

if __name__ == "__main__":
    unittest.main()
