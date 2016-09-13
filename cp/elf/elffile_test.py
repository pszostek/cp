import unittest
import os
from elffile import Kernel, ELFFile

class TestELFFile(unittest.TestCase):

    BIN_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../real_data")

    @classmethod
    def setUpClass(cls):
        cls.kernel = Kernel(os.path.join(cls.BIN_PATH, 'vmlinux.elf'),
                             os.path.join(cls.BIN_PATH, 'vmlinux.symbols'))
        cls.bash = ELFFile(os.path.join(cls.BIN_PATH, 'bash'))
        cls.ko = ELFFile(os.path.join(cls.BIN_PATH, 'nfsv4.ko'))
        cls.glibc = ELFFile(os.path.join(cls.BIN_PATH, 'libc.so.6'))

    def test_get_symbol_by_poff_glibc(self):
        """
         readelf -s:
         9: 000000391cc8d910    30 FUNC    GLOBAL DEFAULT   12 __strspn_c1@@GLIBC_2.2.5
         10: 000000391cc6a5a0   277 FUNC    GLOBAL DEFAULT   12 putwchar@@GLIBC_2.2.5
         11: 000000391cd01d90    23 FUNC    GLOBAL DEFAULT   12 __gethostname_chk@@GLIBC_2.4

         readelf -S:
        [12] .text             PROGBITS         000000391cc1ea60  0001ea60
         00000000001217ac  0000000000000000  AX       0     0     32
        """
        poff_to_sym = {0x8d910: '__strspn_c1',  # first byte, 0x391cc8d910-0x391cc1ea60
                      0x8d910+30-1 : '__strspn_c1', # last byte
                      0x6a5a0: 'putwchar', # first byte
                      0x6a5a0+277-1: 'putwchar', # last byte
                      0x101d90: '__gethostname_chk'
                      }

        for poff, sym in poff_to_sym.iteritems():
            symbol = self.glibc.get_symbol_by_poff(poff)
           # print(poff,symbol,sym)
            self.assertEqual(symbol, sym)

    def test_get_symbol_by_poff_kernel(self):
        """
        symbol map:
        ffffffff81003200 t xen_load_gs_index
        ffffffff81003230 t xen_io_delay
        ffffffff81003240 t xen_apic_read <--
        ffffffff81003250 t xen_apic_icr_read <--
        ffffffff81003260 t xen_apic_wait_icr_idle <-- <--
        ffffffff81003270 t xen_safe_apic_wait_icr_idle
        ffffffff81003280 t xen_write_cr4
        ffffffff810032a0 t xen_write_msr_safe
        ffffffff81003330 t xen_restart
        ffffffff81003360 t xen_emergency_restart
        ffffffff81003390 t xen_machine_halt
        """
        symbol = self.kernel.get_symbol_by_poff(0x203240)
        self.assertEqual(symbol, 'xen_apic_read')

        symbol = self.kernel.get_symbol_by_poff(0x203250)
        self.assertEqual(symbol, 'xen_apic_icr_read')

        symbol = self.kernel.get_symbol_by_poff(0x203261)
        self.assertEqual(symbol, 'xen_apic_wait_icr_idle')

        symbol = self.kernel.get_symbol_by_poff(0x20326f)
        self.assertEqual(symbol, 'xen_apic_wait_icr_idle')

    def test_get_symbol_by_poff_ko(self):
        """
        readelf -s:
         9: 0000000000000000    99 FUNC    LOCAL  DEFAULT    2 nfs4_map_errors
        10: 0000000000000070    59 FUNC    LOCAL  DEFAULT    2 nfs4_call_sync
        13: 0000000000000300   119 FUNC    LOCAL  DEFAULT    2 _nfs4_proc_readlink
        891: 0000000000000000    33 FUNC    GLOBAL DEFAULT    4 cleanup_module
        960: 0000000000000000    79 FUNC    GLOBAL DEFAULT    6 init_module

        readelf -S:
        [Nr] Name              Type             Address           Offset
        Size              EntSize          Flags  Link  Info  Align
        [ 2] .text             PROGBITS         0000000000000000  00000070
        0000000000023974  0000000000000000  AX       0     0     16
        [ 4] .exit.text        PROGBITS         0000000000000000  000239e4
        0000000000000021  0000000000000000  AX       0     0     1
        [ 6] .init.text        PROGBITS         0000000000000000  00023a05
        000000000000004f  0000000000000000  AX       0     0     1

        objdump -d:
        Disassembly of section .text:

            0000000000000000 <nfs4_map_errors>:

        Disassembly of section .exit.text:

            0000000000000000 <cleanup_module>:

        Disassembly of section .init.text:

            0000000000000000 <init_module>:
        """
        poff_to_sym = {0x70+0x0: 'nfs4_map_errors',  # first in .text
                       0x70+20:  'nfs4_map_errors',  # middle of a function
                       0x70+99-1: 'nfs4_map_errors', # last byte
                       0x70+99: None, # beyond last byte
                0x70+0x300: '_nfs4_proc_readlink', # somewhere in .text
                0x239e4+0x0: 'cleanup_module', # in .exit.text
                0x23a05+0x0: 'init_module'} # in .init.text

        for poff, sym in poff_to_sym.iteritems():
            symbol = self.ko.get_symbol_by_poff(poff)
            self.assertEqual(symbol, sym)

    def test_get_symbol_by_poff_bash(self):
        """
        readelf -s:
        200: 000000000047f580   452 FUNC    GLOBAL DEFAULT   14 sh_regmatch
        201: 0000000000439c00   199 FUNC    GLOBAL DEFAULT   14 fatal_error
        202: 00000000004528b0    31 FUNC    GLOBAL DEFAULT   14 set_sigwinch_handler
        203: 00000000004720a0   439 FUNC    GLOBAL DEFAULT   14 set_shellopts
        204: 0000000000431030   167 FUNC    GLOBAL DEFAULT   14 execute_command
        1034: 000000000041b070     0 FUNC    GLOBAL DEFAULT   14 _start # zero size symbol
      """
        poff_to_sym = {0x7f580 : 'sh_regmatch',  # first byte
                       0x7f580 + 452 - 1: 'sh_regmatch',  # last byte
                       0x7f580 + 452: None,  # beyond last byte
                       0x39c00 : 'fatal_error',  # first byte
                       0x39c00 + 199 -1 : 'fatal_error',  # last byte
                       0x31030 : 'execute_command',
                       0x1b070 : '_start'}
        for poff, sym in poff_to_sym.iteritems():
            symbol = self.bash.get_symbol_by_poff(poff)
            self.assertEqual(symbol, sym)

    def test_get_symbol_by_poff_plt_bash(self):
        """
        objdump -d -j .plt | grep @:
            000000000041a410 <tcsetattr@plt>:
            000000000041a420 <chdir@plt>:
            000000000041a430 <fileno@plt>:
            000000000041a440 <dup2@plt>:
            000000000041a460 <mbtowc@plt>:
        """
        poff_to_sym = {0x1a410 : 'tcsetattr',
                       0x1a420 : 'chdir',
                       0x1a430 : 'fileno',
                       0x1a440 : 'dup2',
                       0x1a460 : 'mbtowc'}
        for poff, sym in poff_to_sym.iteritems():
            symbol = self.bash.get_symbol_by_poff(poff)
            #self.assertEqual(symbol, sym)
            print(symbol)

if __name__ == "__main__":
    unittest.main()
